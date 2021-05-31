package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"os"
	"os/exec"
	"time"
	"database/sql"
	"sync"
	"strings"
    _ "github.com/go-sql-driver/mysql"
)

type Daemon struct {
	ID        string
	IPAddress string
	Port      string
}

type Message struct {
	ID      string
	Type    string
	Payload string
}

var masterAddr = "172.22.224.119:3000"
var serverAddr = [3]string { "128.174.246.108:3001", "172.22.224.10:3002", "172.22.224.120:3003" }
var portMap = map[string]string { "172.22.224.119": "3000", "128.174.246.108": "3001", "172.22.224.10": "3002", "172.22.224.120": "3003" }
var isMaster = false
var serverStatus = map[string]bool { "128.174.246.108:3001": false, "172.22.224.10:3002": false, "172.22.224.120:3003": false }
var serverTimeStamp = map[string]int { "128.174.246.108:3001": 0, "172.22.224.10:3002": 0, "172.22.224.120:3003": 0 }
var serverWorkingStatus = map[string]bool { "128.174.246.108:3001": false, "172.22.224.10:3002": false, "172.22.224.120:3003": false }
var db, _ = sql.Open("mysql", "juefeic2:0202141208@/juefeic2_educationtoday")
var mutex = &sync.Mutex{}

func (daemon Daemon) receiver() {
	servaddr, err := net.ResolveUDPAddr("udp", ":"+daemon.Port)
	serv, err := net.ListenUDP("udp", servaddr)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer serv.Close()
	buf := make([]byte, 1024)
	fmt.Println("Receiver is ready!")

	for {
		n, _, err := serv.ReadFromUDP(buf)
		if err != nil {
			fmt.Println(err)
			return
		}
		var message Message
		err = json.Unmarshal(buf[:n], &message)
		if err != nil {
			fmt.Println(err)
			return
		}
		if message.Type == "HEARTBEAT" && isMaster {
			mutex.Lock()
			serverTimeStamp[message.ID] = getTime()
			mutex.Unlock()
		} 
		if message.Type == "DEPARTMENT" {
			fmt.Println("Start working on: " + message.Payload)
			_, err := exec.Command("python3", "algorithm/department/algorithm.py", message.Payload, daemon.IPAddress).Output()
			if err != nil {
				log.Fatal("Error in executing Python script for collecting departments of : " + message.Payload, err)
			}		
			// e.g. 172.22.224.10:3002_Harvard University
			go daemon.sender(masterAddr, "FINISH_DEPARTMENT", daemon.IPAddress + ":" + portMap[daemon.IPAddress] + "_" + message.Payload)
			fmt.Println("Finished " + message.Payload + "\n")
		} 
		if message.Type == "FINISH_DEPARTMENT" {
			// worker_id + university
			s := strings.Split(message.Payload, "_")
			_ = db.QueryRow("update Department_Status set Status = ? where Status = ?", "Finished", s[0]).Scan()
			go storeData("output/" + s[0][:len(s[0]) - 5] + "/" + s[1] + ".json")
			mutex.Lock()
			serverWorkingStatus[s[0]] = false
			mutex.Unlock()
		} 
		if message.Type == "FACULTY" {
			fmt.Println("Start working on: " + message.Payload)
			// message.Payload: Harvard University_Computer Science
			_, err := exec.Command("python3", "algorithm/faculty/algorithm.py", message.Payload, daemon.IPAddress).Output()
			if err != nil {
				log.Fatal("Error in executing Python script for collecting faculty of : " + message.Payload, err)
			}
			// e.g. 172.22.224.10:3002_Harvard University_Computer Science	
			m := strings.Replace(message.Payload, "/", "-slash-", 10)
			go daemon.sender(masterAddr, "FINISH_FACULTY", daemon.IPAddress + ":" + portMap[daemon.IPAddress] + "_" + m)
			fmt.Println("Finished " + message.Payload + "\n")
		} 
		if message.Type == "FINISH_FACULTY" {
			// workerID_university_department
			s := strings.Split(message.Payload, "_")
			_ = db.QueryRow("update Faculty_Status set Status = ? where Status = ?", "Finished", s[0]).Scan()
			go storeData("output/" + s[0][:len(s[0]) - 5] + "/" + s[1] + "_" + s[2] + ".json")
			mutex.Lock()
			serverWorkingStatus[s[0]] = false
			mutex.Unlock()
		}
	}
}

func (daemon Daemon) sender(addr string, messageType string, payload string) {
	s, err := net.ResolveUDPAddr("udp4", addr)
	c, err := net.DialUDP("udp4", nil, s)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer c.Close()
	message := Message{ID: daemon.ID, Type: messageType, Payload: payload}
	m, err := json.Marshal(message)
	_, err = c.Write(m)
	if err != nil {
		fmt.Println(1, err)
		return
	}
}

func (daemon Daemon) heartbeatManager() {
	for {
		if isMaster {
			currentTime := getTime()
			mutex.Lock()
			for k, v := range serverTimeStamp {
				if currentTime - v > 10 {
					if serverStatus[k] {
						fmt.Println(k, " fails...")
						_ = db.QueryRow("update Department_Status set Status = ? where Status = ?", "Fail", k).Scan()
					}
					serverStatus[k] = false
					serverWorkingStatus[k] = false
				} else {
					serverStatus[k] = true
				}
			}
			mutex.Unlock()
		} else {
			go daemon.sender(masterAddr, "HEARTBEAT", "")
		}
		time.Sleep(1 * time.Second)
	}
}

func (daemon Daemon) taskScheduler() {
	for {
		mutex.Lock()
		for k, v := range(serverStatus) {
			if v && !serverWorkingStatus[k] {
				// daemon.scheduleDepartmentTask(k)
				daemon.scheduleFacultyTask(k)
			}
		}
		mutex.Unlock()
		time.Sleep(time.Second)
	}
}

func (daemon Daemon) scheduleFacultyTask (k string) {
	var id string
	var university_name string
	var department_name string
	err := db.QueryRow("select min(University_ID) from Faculty_Status where Status = 'None' and Department_Name like '%Computer Science%';").Scan(&id)
	if err != nil {
		fmt.Println(err)
	}
	_ = db.QueryRow("select University_Name from University where University_ID = ?", id).Scan(&university_name)
	_ = db.QueryRow("select Department_Name from Faculty_Status where University_ID = ? and Status = 'None' and Department_Name like '%Computer Science%'", id).Scan(&department_name)
	_ = db.QueryRow("update Faculty_Status set status = ? where University_ID = ? and Department_Name = ?", k, id, department_name).Scan()
	fmt.Println(university_name, department_name, " -> ", k)
	serverWorkingStatus[k] = true
	go daemon.sender(k, "FACULTY", university_name + "_" + department_name)
}

func (daemon Daemon) scheduleDepartmentTask (k string) {
	var id string
	var university_name string
	err := db.QueryRow("select min(University_ID) from Department_Status where Status = 'None';").Scan(&id)
	if err != nil {
		fmt.Println(err)
	}
	_ = db.QueryRow("select University_Name from University where University_ID = ?", id).Scan(&university_name)
	_ = db.QueryRow("update Department_Status set status = ? where University_ID = ?", k, id).Scan()
	fmt.Println(university_name, " -> ", k)
	serverWorkingStatus[k] = true
	go daemon.sender(k, "DEPARTMENT", university_name)
}

// Daemon main: ./daemon.go <port>
func main() {
	var daemon = new(Daemon)
	daemon.IPAddress = getLocalIP()
	daemon.Port = portMap[daemon.IPAddress]
	daemon.ID = daemon.IPAddress + ":" + daemon.Port
	if daemon.ID == masterAddr {
		fmt.Println("This is Master!")
		isMaster = true
	}
	go daemon.heartbeatManager()
	go daemon.receiver()
	fmt.Printf("Port:%s, IP: %s\n", daemon.Port, daemon.IPAddress)

	if isMaster {
		time.Sleep(3 * time.Second)
		go daemon.taskScheduler()
	}

	scanner := bufio.NewScanner(os.Stdin)
	for scanner.Scan() {
		if scanner.Text() == "ls" {
			fmt.Println("Alive server: ", serverStatus)
			fmt.Println("Server working status: ", serverWorkingStatus)
		}
	}
}
