#include "onnx_engine/SimpleInference.hpp"
#include "network/TcpServer.hpp"
#include <iostream>
#include <memory>
#include <chrono>
#include <thread>
#include <atomic>

using namespace fall_detection;

int main(int argc, char* argv[]) {
    std::cout << "========================================" << std::endl;
    std::cout << "  Fall Detection Backend (Minimal)" << std::endl;
    std::cout << "========================================" << std::endl;
    
    std::string model_path = "models/fall_detection.onnx";
    int port = 8888;
    float confidence_threshold = 0.5f;
    
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--model" && i + 1 < argc) {
            model_path = argv[++i];
        } else if (arg == "--port" && i + 1 < argc) {
            port = std::atoi(argv[++i]);
        } else if (arg == "--confidence" && i + 1 < argc) {
            confidence_threshold = std::atof(argv[++i]);
        } else if (arg == "--help") {
            std::cout << "Usage: " << argv[0] << " [options]" << std::endl;
            std::cout << "Options:" << std::endl;
            std::cout << "  --model <path>       Path to ONNX model" << std::endl;
            std::cout << "  --port <port>        TCP port (default: 8888)" << std::endl;
            std::cout << "  --confidence <val>   Confidence threshold (default: 0.5)" << std::endl;
            std::cout << "  --help               Show this help" << std::endl;
            return 0;
        }
    }
    
    std::cout << "Configuration:" << std::endl;
    std::cout << "  Model: " << model_path << std::endl;
    std::cout << "  Port: " << port << std::endl;
    std::cout << "  Confidence: " << confidence_threshold << std::endl;
    std::cout << "----------------------------------------" << std::endl;
    
    try {
        // Charger le modele ONNX
        std::cout << "\n[1/2] Loading ONNX model..." << std::endl;
        auto inference_engine = std::make_unique<SimpleInference>(model_path);
        
        if (!inference_engine->load()) {
            std::cerr << "Failed to load ONNX model" << std::endl;
            return 1;
        }
        
        inference_engine->setConfidenceThreshold(confidence_threshold);
        std::cout << "OK: Model loaded" << std::endl;
        
        // Demarrer le serveur TCP
        std::cout << "\n[2/2] Starting TCP server..." << std::endl;
        auto tcp_server = std::make_unique<network::TcpServer>(port);
        tcp_server->setInferenceEngine(inference_engine.get());
        
        std::atomic<uint64_t> total_detections{0};
        
        tcp_server->setDetectionCallback([&total_detections](const std::vector<Detection>& detections) {
            total_detections += detections.size();
            std::cout << "Detections: " << detections.size() << " (Total: " << total_detections << ")" << std::endl;
        });
        
        if (!tcp_server->start()) {
            std::cerr << "Failed to start TCP server" << std::endl;
            return 1;
        }
        
        std::cout << "\n========================================" << std::endl;
        std::cout << "  Server running on port " << port << std::endl;
        std::cout << "  Waiting for Python client..." << std::endl;
        std::cout << "========================================" << std::endl;
        std::cout << "\nPress Ctrl+C to stop\n" << std::endl;
        
        // Boucle principale
        while (true) {
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
        
        tcp_server->stop();
        std::cout << "\nShutdown complete" << std::endl;
        return 0;
        
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }
}
