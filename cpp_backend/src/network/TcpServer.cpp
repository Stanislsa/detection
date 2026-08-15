#include "network/TcpServer.hpp"
#include <iostream>
#include <cstring>

namespace fall_detection {
namespace network {

TcpServer::TcpServer(int port)
    : port_(port)
    , running_(false)
#ifdef _WIN32
    , server_socket_(INVALID_SOCKET)
#else
    , server_socket_(-1)
#endif
    , inference_engine_(nullptr)
{
}

TcpServer::~TcpServer() {
    stop();
}

bool TcpServer::start() {
    if (!initWinsock()) {
        return false;
    }
    
#ifdef _WIN32
    server_socket_ = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (server_socket_ == INVALID_SOCKET) {
        std::cerr << "[TcpServer] Failed to create socket" << std::endl;
        return false;
    }
#else
    server_socket_ = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket_ < 0) {
        std::cerr << "[TcpServer] Failed to create socket" << std::endl;
        return false;
    }
#endif
    
    sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port_);
    
#ifdef _WIN32
    if (bind(server_socket_, (sockaddr*)&server_addr, sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "[TcpServer] Failed to bind socket" << std::endl;
        closesocket(server_socket_);
        return false;
    }
#else
    if (bind(server_socket_, (sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "[TcpServer] Failed to bind socket" << std::endl;
        close(server_socket_);
        return false;
    }
#endif
    
#ifdef _WIN32
    if (listen(server_socket_, 1) == SOCKET_ERROR) {
        std::cerr << "[TcpServer] Failed to listen" << std::endl;
        closesocket(server_socket_);
        return false;
    }
#else
    if (listen(server_socket_, 1) < 0) {
        std::cerr << "[TcpServer] Failed to listen" << std::endl;
        close(server_socket_);
        return false;
    }
#endif
    
    running_ = true;
    server_thread_ = std::thread(&TcpServer::serverLoop, this);
    
    std::cout << "[TcpServer] Listening on port " << port_ << std::endl;
    return true;
}

void TcpServer::stop() {
    running_ = false;
    
#ifdef _WIN32
    if (server_socket_ != INVALID_SOCKET) {
        closesocket(server_socket_);
        server_socket_ = INVALID_SOCKET;
    }
#else
    if (server_socket_ >= 0) {
        close(server_socket_);
        server_socket_ = -1;
    }
#endif
    
    if (server_thread_.joinable()) {
        server_thread_.join();
    }
    
    cleanupWinsock();
}

void TcpServer::serverLoop() {
    while (running_) {
#ifdef _WIN32
        SOCKET client_socket = accept(server_socket_, nullptr, nullptr);
        if (client_socket == INVALID_SOCKET) {
            if (running_) {
                std::cerr << "[TcpServer] Accept failed" << std::endl;
            }
            continue;
        }
#else
        int client_socket = accept(server_socket_, nullptr, nullptr);
        if (client_socket < 0) {
            if (running_) {
                std::cerr << "[TcpServer] Accept failed" << std::endl;
            }
            continue;
        }
#endif
        
        std::cout << "[TcpServer] Client connected" << std::endl;
        
        // Recevoir les dimensions de l'image
        int header[3]; // width, height, channels
#ifdef _WIN32
        int received = recv(client_socket, (char*)header, sizeof(header), 0);
        if (received != sizeof(header)) {
            closesocket(client_socket);
            continue;
        }
#else
        int received = recv(client_socket, header, sizeof(header), 0);
        if (received != sizeof(header)) {
            close(client_socket);
            continue;
        }
#endif
        
        int width = header[0];
        int height = header[1];
        int channels = header[2];
        
        std::cout << "[TcpServer] Image: " << width << "x" << height << "x" << channels << std::endl;
        
        // Recevoir les données de l'image
        int image_size = width * height * channels;
        std::vector<uint8_t> image_data(image_size);
        
        int total_received = 0;
        while (total_received < image_size) {
#ifdef _WIN32
            int bytes = recv(client_socket, (char*)(image_data.data() + total_received), image_size - total_received, 0);
#else
            int bytes = recv(client_socket, image_data.data() + total_received, image_size - total_received, 0);
#endif
            if (bytes <= 0) {
                break;
            }
            total_received += bytes;
        }
        
        if (total_received == image_size && inference_engine_) {
            // Inferer
            auto detections = inference_engine_->infer(image_data.data(), width, height);
            
            // Envoyer les detections
            int num_detections = detections.size();
#ifdef _WIN32
            send(client_socket, (char*)&num_detections, sizeof(num_detections), 0);
#else
            send(client_socket, &num_detections, sizeof(num_detections), 0);
#endif
            
            for (const auto& det : detections) {
                float det_data[7] = {
                    det.x, det.y, det.width, det.height,
                    det.confidence,
                    static_cast<float>(det.class_id),
                    0.0f
                };
#ifdef _WIN32
                send(client_socket, (char*)det_data, sizeof(det_data), 0);
#else
                send(client_socket, det_data, sizeof(det_data), 0);
#endif
            }
            
            if (detection_callback_) {
                detection_callback_(detections);
            }
        }
        
#ifdef _WIN32
        closesocket(client_socket);
#else
        close(client_socket);
#endif
        
        std::cout << "[TcpServer] Client disconnected" << std::endl;
    }
}

void TcpServer::handleClient() {
}

bool TcpServer::initWinsock() {
#ifdef _WIN32
    WSADATA wsa_data;
    if (WSAStartup(MAKEWORD(2, 2), &wsa_data) != 0) {
        std::cerr << "[TcpServer] WSAStartup failed" << std::endl;
        return false;
    }
#endif
    return true;
}

void TcpServer::cleanupWinsock() {
#ifdef _WIN32
    WSACleanup();
#endif
}

} // namespace network
} // namespace fall_detection
