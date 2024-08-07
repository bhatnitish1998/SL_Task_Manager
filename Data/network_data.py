import os
import time
import json
import datetime
from Data.utility_functions import kb_to_print, b_to_print, bytes_to_kilobytes, bytes_to_megabytes, bytes_to_gigabytes


class NetworkInfo:
    """
    A class that provides information about network usage.

    Attributes:
        stat_file (str): The path to the file containing network statistics.
        exclude_interfaces (List[str]): A list of interface names to exclude from the statistics.

    Methods:
        get_network_usage(): Returns a dictionary containing the network usage statistics.
    """

    def __init__(self, exclude_interfaces: list = []) -> None:
        """
        Initializes a new instance of the NetworkInfo class.

        Args:
            exclude_interfaces (List[str]): A list of interface names to exclude from the statistics.
        """
        self.stat_file = "/proc/net/dev"
        self.exclude_interfaces = exclude_interfaces

        self.stat_fd = self._get_stat_file()
        self.startup_stats = {}
        self.previous_stat_data = self._parse_stat_data()
        self.previous_timestamp = datetime.datetime.now()

    def _get_stat_file(self):
        """
        Opens the network statistics file and returns a file descriptor.
        """
        return open(self.stat_file, "r")

    def _get_stat_file_data(self):
        """
        Reads the network statistics file and returns its contents as a string.
        """
        self.stat_fd.seek(0)
        return self.stat_fd.read()

    @property
    def stat_data(self):
        """
        A property that returns the latest contents of the network statistics file.
        """
        return self._get_stat_file_data()

    def _parse_stat_data(self):
        """
        Parses the network statistics data and returns a dictionary with the network usage stats.
        """
        data = self.stat_data.split("\n")
        data = [i.split() for i in data[2:] if i != ""]
        # print(json.dumps(data, indent=2))
        network_data = {}
        for row in data:
            interface = row[0][:-1]
            if interface in self.exclude_interfaces:
                continue

            interface_data = {}

            interface_data["rx_bytes"] = int(row[1])
            interface_data["rx_packets"] = int(row[2])
            interface_data["rx_errors"] = int(row[3])
            interface_data["rx_drop"] = int(row[4])
            interface_data["rx_fifo"] = int(row[5])
            interface_data["rx_frame"] = int(row[6])
            interface_data["rx_compressed"] = int(row[7])
            interface_data["rx_multicast"] = int(row[8])
            interface_data["tx_bytes"] = int(row[9])
            interface_data["tx_packets"] = int(row[10])
            interface_data["tx_errors"] = int(row[11])
            interface_data["tx_drop"] = int(row[12])
            interface_data["tx_fifo"] = int(row[13])
            interface_data["tx_frame"] = int(row[14])
            interface_data["tx_compressed"] = int(row[15])
            interface_data["tx_multicast"] = int(row[16])

            network_data[interface] = interface_data

        # print(json.dumps(network_data, indent=2))
        return network_data

    def _get_network_info(self):
        network_info = []

        for interface in self.previous_stat_data.keys():
            # parts = line.split(":")
            # interface = parts[0].strip()
            interface_data = {"interface": interface,
                              "addresses": []}

            # Get IP addresses and MAC addresses for each interface
            try:
                iface_info = os.popen(f"ip addr show {interface}").read()
                for line in iface_info.split('\n'):
                    if 'inet' in line:
                        ip_address = line.split(' ')[5]
                        netmask = line.split('/')[1]
                        interface_data["addresses"].append(
                            {"ip_address": ip_address, "netmask": netmask})
                    elif 'link/ether' in line:
                        mac_address = line.strip().split(' ')[1]
                        interface_data["mac_address"] = mac_address
            except FileNotFoundError:
                pass  # Handle exception if 'ip' command is not available

            network_info.append(interface_data)

        network_usage = self.get_network_usage()
        network_info_formatted = []
        for interface_info in network_info:
            interface = interface_info["interface"]
            info = interface_info

            if interface not in self.startup_stats.keys():
                self.startup_stats[interface] = {
                    "tx_B": network_usage[interface]["tx_B"],
                    "rx_B": network_usage[interface]["rx_B"],
                }

            network_info_formatted.append([
                interface,
                info["addresses"][0]["ip_address"] if len(
                    info["addresses"]) else "",
                info["mac_address"] if "mac_address" in info else "",
                b_to_print(
                    network_usage[interface]["tx_B"] - self.startup_stats[interface]["tx_B"]),
                b_to_print(
                    network_usage[interface]["rx_B"] - self.startup_stats[interface]["rx_B"]),
            ])

        return network_info_formatted

    def get_network_usage(self):
        current_network_data = self._parse_stat_data()
        current_timestamp = datetime.datetime.now()
        time_delta = current_timestamp - self.previous_timestamp

        network_usage = {}
        network_usage["total"] = {"rx_Bps": 0,
                                  "tx_Bps": 0, "rx_B": 0, "tx_B": 0}

        for interface, interface_stat in current_network_data.items():
            network_usage[interface] = {}
            delta_rx_bytes = (
                interface_stat["rx_bytes"] -
                self.previous_stat_data[interface]["rx_bytes"]
            )
            delta_tx_bytes = (
                interface_stat["tx_bytes"] -
                self.previous_stat_data[interface]["tx_bytes"]
            )
            network_usage[interface]["rx_B"] = interface_stat["rx_bytes"]
            network_usage[interface]["tx_B"] = interface_stat["tx_bytes"]

            rx_bytes_per_second = round(
                delta_rx_bytes / time_delta.total_seconds(), 2)
            tx_bytes_per_second = round(
                delta_tx_bytes / time_delta.total_seconds(), 2)

            rx_kilobytes_per_second = round(
                bytes_to_kilobytes(rx_bytes_per_second), 2)
            rx_mega_bytes_per_second = round(
                bytes_to_megabytes(rx_bytes_per_second), 2)
            tx_kilobytes_per_second = round(
                bytes_to_kilobytes(tx_bytes_per_second), 2)
            tx_mega_bytes_per_second = round(
                bytes_to_megabytes(tx_bytes_per_second), 2)

            network_usage[interface]["rx_KBps"] = rx_kilobytes_per_second
            network_usage[interface]["rx_MBps"] = rx_mega_bytes_per_second
            network_usage[interface]["tx_KBps"] = tx_kilobytes_per_second
            network_usage[interface]["tx_MBps"] = tx_mega_bytes_per_second

            network_usage["total"]["rx_B"] += interface_stat["rx_bytes"]
            network_usage["total"]["tx_B"] += interface_stat["tx_bytes"]
            network_usage["total"]["rx_Bps"] += rx_bytes_per_second
            network_usage["total"]["tx_Bps"] += tx_bytes_per_second

        network_usage["total"]["rx_KBps"] = round(
            bytes_to_kilobytes(network_usage["total"]["rx_Bps"]), 2)
        network_usage["total"]["rx_MBps"] = round(
            bytes_to_megabytes(network_usage["total"]["rx_Bps"]), 2)
        network_usage["total"]["tx_KBps"] = round(
            bytes_to_kilobytes(network_usage["total"]["tx_Bps"]), 2)
        network_usage["total"]["tx_MBps"] = round(
            bytes_to_megabytes(network_usage["total"]["tx_Bps"]), 2)

        self.previous_stat_data = current_network_data
        self.previous_timestamp = current_timestamp
        return network_usage

    def get_interfaces(self):
        return self._parse_stat_data().keys()

    @ property
    def network_info(self):
        return self._get_network_info()

    def __del__(self):
        self.stat_fd.close()
