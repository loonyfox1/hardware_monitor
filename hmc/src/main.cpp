#define _GNU_SOURCE
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <numeric>
#include <vector>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
	int sock;
    struct sockaddr_in addr;

    sock = socket(AF_INET, SOCK_STREAM, 0);
    if(sock < 0)
    {
        perror("socket");
        exit(1);
    }

    addr.sin_family = AF_INET;
    addr.sin_port = htons(3425); // или любой другой порт...
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

	// FILE *cpuinfo = fopen("/proc/cpuinfo","rb");
	char *arg = 0;
	size_t size = 0;

	long founds,foundf;
	
	if(connect(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0)
		{
			perror("connect");
			exit(2);
		}

	while(1){
		FILE *cpuinfo = fopen("/proc/cpuinfo","rb");
		arg = 0;
		getdelim(&arg, &size, 0, cpuinfo);
		// while(getdelim(&arg, &size, 0, cpuinfo) != -1){
		// 	puts(arg);	
		// }

		std::vector<std::string> freq;
		founds = 0;
		foundf = 0;
		while(founds != std::string::npos){
			
			founds = std::string(arg).find("cpu MHz",founds+1);
			foundf = std::string(arg).find("\n",founds+1);
			// std::cout << arg << std::endl;
			if (founds != std::string::npos){
				// std::cout << "yeah" << std::endl;
				// std::cout << std::string(arg).substr(founds+11,foundf-founds-11) << std::endl;
				freq.push_back(std::string(arg).substr(founds+11,foundf-founds-11));
				freq.push_back(" ");
			}
		}

		// freq.push_back("\n");
		std::string msg;
		msg = accumulate(begin(freq), end(freq), msg);
		char *cstr = &msg[0u];
		std::cout << cstr << std::endl;

		send(sock, cstr, sizeof(cstr)*freq.size(), 0);
		free(arg);
		fclose(cpuinfo);
		usleep(1000000);
		
	}

    close(sock);

	// free(arg);
	// fclose(cpuinfo);
	return 0;
}

