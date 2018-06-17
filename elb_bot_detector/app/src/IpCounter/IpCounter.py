class IpCounter():
    
    @staticmethod
    def processIp(ip, ip_hash_map):
        if ip in ip_hash_map:
            ip_hash_map[ip] = ip_hash_map[ip] + 1
        else:
            ip_hash_map[ip] = 1
        return ip_hash_map
