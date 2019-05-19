#include <iostream>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <stdlib.h>
#include <string>
#include <numeric>
#include <vector>

const int BUF_SIZE = 2048;

int main(int argc, char *argv[]) {
	int sock, listener;
    struct sockaddr_in addr;
    char buf[BUF_SIZE];
    int bytes_read;
	int founds, foundf;

    listener = socket(AF_INET, SOCK_STREAM, 0);
    if(listener < 0)
    {
        perror("socket");
        exit(1);
    }
    
    addr.sin_family = AF_INET;
    addr.sin_port = htons(3425);
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    if(bind(listener, (struct sockaddr *)&addr, sizeof(addr)) < 0)
    {
        perror("bind");
        exit(2);
    }

    listen(listener, 1);
    
    while(1)
    {
        sock = accept(listener, NULL, NULL);
        if(sock < 0)
        {
            perror("accept");
            exit(3);
        }
        while(1)
        {
			std::vector<double> data;
            bytes_read = recv(sock, buf, BUF_SIZE, 0);
            if(bytes_read <= 0) break;
			std::cout << buf << std::endl;

			std::string str = std::string(buf).substr(0,sizeof(buf));
			founds = 0;
			foundf = 0;
			while(foundf != std::string::npos){
				foundf = str.find(" ",founds);
				// std::cout << foundf << std::endl;
				if (foundf != std::string::npos){
					data.push_back(std::stof(str.substr(founds,foundf-founds)));
				}
				founds = foundf+1;
			}
        }
    
        close(sock);
    }
    
    return 0;
}