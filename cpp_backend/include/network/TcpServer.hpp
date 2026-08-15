#pragma once

#ifdef _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#endif

#include <string>
#include <thread>
#include <functional>
#include <atomic>
#include <vector>

#include "onnx_engine/SimpleInference.hpp"

namespace fall_detection {
namespace network {

class TcpServer {
public:
    using DetectionCallback = std::function<void(const std::vector<Detection>&)>;

    TcpServer(int port = 8888);
    ~TcpServer();
    
    bool start();
    void stop();
    
    void setInferenceEngine(SimpleInference* engine) { inference_engine_ = engine; }
    void setDetectionCallback(DetectionCallback callback) { detection_callback_ = callback; }

private:
    int port_;
    bool running_;
    std::thread server_thread_;
    
#ifdef _WIN32
    SOCKET server_socket_;
#else
    int server_socket_;
#endif
    
    SimpleInference* inference_engine_;
    DetectionCallback detection_callback_;
    
    void serverLoop();
    void handleClient();
    
    bool initWinsock();
    void cleanupWinsock();
};

} // namespace network
} // namespace fall_detection
