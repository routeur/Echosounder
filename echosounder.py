#! /usr/bin/env python

from typing import Optional, List, Tuple
import json
import platform
import nmap
import scapy
from scapy.arch import get_if_addr, get_if_hwaddr
from scapy.config import conf
from scapy.layers.inet import IP, ICMP
from scapy.layers.l2 import getmacbyip
from scapy.packet import Packet
from scapy.sendrecv import srp


def template() -> dict:
    """
    grab the
        - IP and mac of local machine
        - gateway IP
    """
    local_ip: str = get_if_addr(conf.iface)
    local_mac: str = get_if_hwaddr(conf.iface)

    router_hop_1: Optional[str] = conf.route.route("0.0.0.0")[2]
    router_hop_1_mac: Optional[str] = getmacbyip(router_hop_1)
    return {"local_ip": local_ip, "local_mac": local_mac, "gateway_ip": router_hop_1, "gateway_mac": router_hop_1_mac}


def arp_local_scan(target_ip) -> tuple:
    """
    ARP SCAN for local machines
    """
    router_hop_1: Optional[str] = conf.route.route("0.0.0.0")[2]
    # retrieve local IP address
    # 172.20.10.4/28 -- 192.168.1.0/24
    arp = scapy.layers.l2.ARP(pdst=target_ip)

    # ff:ff:ff:ff:ff:ff broadcast mac address
    ether = scapy.layers.l2.Ether(dst="ff:ff:ff:ff:ff:ff")

    # stack the protocols
    packet = ether / arp
    result: tuple = srp(packet, timeout=3, verbose=0)[0]

    # initialisation de la liste des clients
    clients: List[dict] = []
    ip_list: List[str] = []
    mac_list: List[str] = []
    ip_list.append(scapy.arch.get_if_addr(conf.iface))
    mac_list.append(scapy.arch.get_if_hwaddr(conf.iface))

    for sent, received in result:  # all the responses are implemented in "clients"
        clients.append({'ip': received.psrc, 'mac': received.hwsrc})
    for client in clients:  # display the clients
        ip_list.append((client['ip']))
        mac_list.append((client['mac']))
    # mac = getmacbyip(ip) get mac adress with IP
    return ip_list, mac_list, router_hop_1


def out_in_json(machine) -> tuple:
    nm: nmap.PortScanner = nmap.PortScanner()
    nmap_scan_result: dict = nm.scan(hosts=machine, arguments='-O')
    scan_res_to_str: str = json.dumps(nmap_scan_result)
    scan_res_to_dict = json.loads(scan_res_to_str)

    try:
        name: str = scan_res_to_dict["scan"][machine]["osmatch"][0]["name"]
        vendor: str = scan_res_to_dict["scan"][machine]["osmatch"][0]["osclass"][0]["vendor"]
        osfamily: str = scan_res_to_dict["scan"][machine]["osmatch"][0]["osclass"][0]["osfamily"]
        accuracy: str = scan_res_to_dict["scan"][machine]["osmatch"][0]["accuracy"]
    except:
        name = "unknown"
        vendor = "unknown"
        osfamily = "unknown"
        accuracy = "unknown"
    return name, vendor, osfamily, accuracy


def device_profiling(ip_addresses) -> List[dict]:
    machine_specs: List[dict] = []
    for current_ip in ip_addresses:
        machine_specs.append(creation_data_nmap(current_ip))
    return machine_specs


def recon_fast_ping(target_ip) -> tuple:
    os_ttl_list: List[str] = [platform.system()]
    local_ip: str = scapy.arch.get_if_addr(conf.iface)
    ttl_list: list = []
    ip_list, mac = ip_mac_from_arp_local_scan(target_ip)

    for ip in ip_list:
        if ip == local_ip:
            ttl_list.append('0')
        else:
            packet: Optional[Packet] = scapy.sendrecv.sr1(IP(dst=ip) / ICMP(), timeout=15)
            if packet is None:
                ttl_list.append('0')
            else:
                ttl_list.append(packet.ttl)

    append_os_ttl(os_ttl_list, ttl_list)
    return ip_list, mac, os_ttl_list


def ip_mac_from_arp_local_scan(target_ip) -> Tuple[List[str], List[str]]:
    scan_result: tuple = arp_local_scan(target_ip)
    ip_list: List[str] = scan_result[0]
    mac: List[str] = scan_result[1]
    return ip_list, mac


def append_os_ttl(os_ttl_list, ttl_list) -> None:
    for z in range(len(ttl_list)):
        if ttl_list[z] == 64 or ttl_list[z] == 255:
            os_ttl_list.append("Linux/UNIX")
        elif ttl_list[z] == 128:
            os_ttl_list.append("Windows")
        elif ttl_list[z] == 254:
            os_ttl_list.append("Cisco")
        else:
            os_ttl_list.append("Unknow")


def creation_data_nmap(ip_address) -> dict:
    machine_specs: tuple = out_in_json(ip_address)
    return {
        "IP": ip_address,
        "nom": machine_specs[0],
        "vendeur": machine_specs[1],
        "osfamily": machine_specs[2],
        "accuracy": machine_specs[3],
    }


def retrieve_ip_mac_os_from_scan(target_ip, scan_type: str = "ARP") -> tuple:
    """
    Function that retrieves the IP, Mac, OS from a scan and return them
    """
    if scan_type == "ARP":
        scan_result: tuple = arp_local_scan(target_ip)
        os_list: None = None
    elif scan_type == "FAST_PING":  # FAST_PING
        scan_result: tuple = recon_fast_ping(target_ip)
        os_list: List[str] = scan_result[2]
    else:
        raise NotImplementedError(f"This scan has not been implemented yet, "
                                  f"or wrong parameter '{scan_type}'")
    ip_list: List[str] = scan_result[0]
    mac_list: List[str] = scan_result[1]
    global_list: List[dict] = []
    return ip_list, mac_list, os_list, global_list


def data_creation_arp_scan(target_ip) -> List[dict]:
    ip_list, mac_list, os_list, global_list = retrieve_ip_mac_os_from_scan(target_ip, scan_type="ARP")

    for i in range(len(ip_list)):
        current_ip: str = ip_list[i]
        current_mac: str = mac_list[i]
        ip_and_mac_to_dict = {
            "IP": current_ip,
            "mac": current_mac,
        }
        global_list.append(ip_and_mac_to_dict)
    return global_list


def data_creation_fast_ping(target_ip) -> List[dict]:
    ip_list, mac_list, os_list, global_list = retrieve_ip_mac_os_from_scan(target_ip, scan_type="FAST_PING")

    for i in range(len(ip_list)):
        current_ip: str = ip_list[i]
        current_mac: str = mac_list[i]
        current_os: str = os_list[i]
        result = {
            "IP": current_ip,
            "mac": current_mac,
            "OS": current_os,
        }
        global_list.append(result)
    return global_list


if __name__ == "__main__":
    print("TEST")
    data_creation_fast_ping('192.168.1.0/24')