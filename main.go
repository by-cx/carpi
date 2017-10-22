package main

import (
    "github.com/kidoman/embd/controller/pca9685"
    "github.com/kidoman/embd"
     _ "github.com/kidoman/embd/host/rpi" // This loads the RPi driver
     "time"
     "log"
     "net"
     "strconv"
     "strings"
)

const (
    MAX = 4096
    PORT = "1234"
    BORDER_MIN = 1500
    BORDER_MAX = 3500
    NEUTRAL = 2500
    NANOSECS = 10000000
)


type Speed struct {
    // Power on wheel (0 - 100)
    wheelFrontLeft int
    wheelFrontRight int
    wheelRearLeft int
    wheelRearRight int
    lastUpdate int64
}

var conn *net.UDPConn
var speed *Speed
var pca *pca9685.PCA9685

func doErr(err error) {
    if err != nil {
        log.Fatalln(err)
    }
}

func init() {
    var err error

    log.Println("UDP socket initialization")
    addr, err := net.ResolveUDPAddr("udp4", ":"+PORT)
    doErr(err)
    conn, err = net.ListenUDP("udp4", addr)
    doErr(err)

    log.Println("PCA 9685 libary initialization")
    bus := embd.NewI2CBus(1)
    pca = pca9685.New(bus, 0x40)
    pca.Freq = 400
    pca.Wake()
    time.Sleep(200 * time.Millisecond)

    speed = &Speed{
        wheelFrontLeft: 0,
        wheelFrontRight: 0,
        wheelRearLeft: 0,
        wheelRearRight: 0,
    }

    go keepTheSpeed()
}

func performanceToValue(performance int) int {
    if performance >= -5 && performance <= 5 {
        return NEUTRAL
    } else {
        return performance * 10 + NEUTRAL
    }
}

func keepTheSpeed() {
    log.Println("Keep the speed process begins")
    for {
        if (time.Now().UnixNano() - speed.lastUpdate) > 50*NANOSECS {
            //Safety
            pca.SetPwm(0, 0, NEUTRAL)
            pca.SetPwm(1, 0, NEUTRAL)
            pca.SetPwm(2, 0, NEUTRAL)
            pca.SetPwm(3, 0, NEUTRAL)
            log.Println("No signal, going neutral")
        } else {
            log.Println(performanceToValue(speed.wheelFrontLeft))
            pca.SetPwm(0, 0, performanceToValue(speed.wheelFrontLeft))
            pca.SetPwm(1, 0, performanceToValue(speed.wheelFrontRight))
            pca.SetPwm(2, 0, performanceToValue(speed.wheelRearLeft))
            pca.SetPwm(3, 0, performanceToValue(speed.wheelRearRight))
            log.Println("Setting a new values in PWM generator")
        }

        time.Sleep(50 * time.Millisecond)
    }
}

func processCommand(command []byte) {
    strCommand := strings.Trim(string(command), " \n")

    var value0 int
    var value1 int
    var value2 int
    var value3 int
    var err error

    parts := strings.Split(strCommand, " ")

    if parts[0] == "go" {
        value0, err = strconv.Atoi(parts[1])
        if err != nil {
            log.Println("Can't convert to int ("+parts[1]+")")
            return
        }
        value1, err = strconv.Atoi(parts[2])
        if err != nil {
            log.Println("Can't convert to int ("+parts[2]+")")
            return
        }
        value2, err = strconv.Atoi(parts[3])
        if err != nil {
            log.Println("Can't convert to int ("+parts[3]+")")
            return
        }
        value3, err = strconv.Atoi(parts[4])
        if err != nil {
            log.Println("Can't convert to int ("+parts[4]+")")
            return
        }

        log.Println("Setting a new values in speed structure")
        speed.wheelFrontLeft = value0
        speed.wheelFrontRight = value1
        speed.wheelRearLeft = value2
        speed.wheelRearRight = value3
        speed.lastUpdate = time.Now().UnixNano()
        log.Println("New speed strucuture values", speed)
    } else {
        log.Println("Uknown command ("+strCommand+")")
    }
}

func main() {
    defer conn.Close()
    defer pca.Close()

    log.Println("Let's go")

    buf := make([]byte, 1024)
    var n int
    var err error

    for {
        n, _, err = conn.ReadFromUDP(buf)
        if n != 0 {
            //log.Println("Received ",string(buf[0:n]))
            processCommand(buf[0:n])
        }

        if err != nil {
            log.Println("Error: ",err)
        }
    }

    /*pca.SetPwm(0, 0, 2500)
    time.Sleep(2*time.Second)
    pca.SetPwm(0, 0, 3500)
    time.Sleep(2*time.Second)
    pca.SetPwm(0, 0, 2500)*/


}
