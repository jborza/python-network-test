import threading
from scapy.all import ICMP, IP, sr1, sendp, Ether
import time
import statistics
import matplotlib.pyplot as plt


def plot_results():
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))
    fig.suptitle('Network Performance Metrics') 
    
    ax1.plot(latenc_results, marker='o')
    ax1.set_title('Latency (ms)')
    ax1.set_xlabel('Ping attempt')
    ax1.set_ylabel('Latency (ms)')
    ax1.grid(True)
    
    ax2.bar(['Packet loss', 'Packet received'],
            [packet_loss_count, 
            len(latenc_results) - packet_loss_count],
            color=['red', 'green'])
    ax2.set_title('Packet loss rate')
    ax2.set_ylabel('Number of packets')
    ax2.grid(True)
    
    if(total_packets_sent > 0):
        bandwidth = total_packets_sent * 1000 * 8 / 5 / 1024 # kbps
        ax3.bar(['Bandwidth'], [bandwidth], color=['blue'])
        ax3.set_title('Estimated bandwidth')
        ax3.set_ylabel('Bandwidth (Kbps)')
        ax3.grid(True)
    else:
        ax3.axis('off')
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()
    
    

def ping(ip):
    packet = Ether()/IP(dst=ip)/ICMP()
    rtt = []
    for i in range(10):
        start = time.time()
        sendp(packet)
        rtt.append(time.time() - start)
    print(f"RTT: {statistics.mean(rtt)}")

# global variables to hold measurement results
latenc_results = []
packet_loss_count = 0
total_packets_sent = 0

# function to measure latency
def measure_latency(target_ip, count=5):
    global latenc_results
    for _ in range(count):
        start_time = time.time()
        reply = sr1(IP(dst=target_ip)/ICMP(), timeout=2, verbose=0)
        if reply:
            round_trip_time = (time.time() - start_time) * 1000  # convert to ms
            latenc_results.append(round_trip_time)
        else:
            global packet_loss_count
            packet_loss_count += 1

        time.sleep(1)

# function to measure bandwidth by sending packets and measuring bandwidth, measuring return rate


def measure_bandwidth(target_ip, size=1000, duration=5):
    start_time = time.time()
    packets_sent = 0
    while time.time() - start_time < duration:
        sendp(Ether()/IP(dst=target_ip)/ICMP()/("X"*size), verbose=0)
        packets_sent += 1
        time.sleep(0.1)  # send 10 packets per second
    global total_packets_sent
    total_packets_sent = packets_sent

def print_results():
    if latenc_results:
        print(f"Average latency: {statistics.mean(latenc_results)} ms")
        print(f"Maximum latency: {max(latenc_results)} ms")
        print(f"Minimum latency: {min(latenc_results)} ms")
        print(f"Packet loss rate: {(packet_loss_count / len(latenc_results) * 100):2f}%")
    if total_packets_sent > 0:
        print(f"Bandwidth: {total_packets_sent * 1000 * 8 / 5 / 1024:2f} Mbps")

def main(target_ip):
    threads = []
    threads.append(threading.Thread(target=measure_latency, args=(target_ip,)))
    threads.append(threading.Thread(target=measure_bandwidth, args=(target_ip,)))
    
    # start all threads
    for thread in threads:
        thread.start()
        
    # wait for all threads to finish
    for thread in threads:
        thread.join()
        
    print_results()
    plot_results()
    pass


if __name__ == "__main__":
    target_ip = "8.8.8.8"
    main(target_ip)
