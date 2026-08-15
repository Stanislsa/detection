#include "onnx_engine/SimpleInference.hpp"
#include <iostream>
#include <algorithm>
#include <cstring>
#include <string>

namespace fall_detection {

SimpleInference::SimpleInference(const std::string& model_path)
    : model_path_(model_path)
    , env_(nullptr)
    , session_(nullptr)
    , memory_info_(nullptr)
{
}

SimpleInference::~SimpleInference() {
    // Les noms sont gérés par les smart pointers, pas besoin de free manuel
}

bool SimpleInference::load() {
    try {
        env_ = std::make_unique<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "FallDetection");
        
        Ort::SessionOptions session_options;
        session_options.SetIntraOpNumThreads(1);
        session_options.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_EXTENDED);
        
        // Convertir le chemin en wchar_t pour ONNX Runtime 1.28.0
        std::wstring model_path_w(model_path_.begin(), model_path_.end());
        session_ = std::make_unique<Ort::Session>(*env_, model_path_w.c_str(), session_options);
        
        Ort::AllocatorWithDefaultOptions allocator;
        
        // Utiliser l'API correcte pour ONNX Runtime 1.28.0
        auto input_name_ptr = session_->GetInputNameAllocated(0, allocator);
        auto output_name_ptr = session_->GetOutputNameAllocated(0, allocator);
        
        input_name_ = std::string(input_name_ptr.get());
        output_name_ = std::string(output_name_ptr.get());
        
        memory_info_ = std::make_unique<Ort::MemoryInfo>(Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault));
        
        std::cout << "[SimpleInference] Model loaded: " << model_path_ << std::endl;
        return true;
        
    } catch (const Ort::Exception& e) {
        std::cerr << "[SimpleInference] ONNX Runtime error: " << e.what() << std::endl;
        return false;
    }
}

std::vector<Detection> SimpleInference::infer(
    const uint8_t* image_data,
    int width,
    int height
) {
    std::vector<Detection> detections;
    
    if (!session_) {
        std::cerr << "[SimpleInference] Session not loaded" << std::endl;
        return detections;
    }
    
    try {
        const int input_size = 640 * 640 * 3;
        std::vector<float> input_tensor_values(input_size);
        
        // Resize et normalisation (simple nearest neighbor)
        for (int i = 0; i < 640 * 640; ++i) {
            int src_x = (i % 640) * width / 640;
            int src_y = (i / 640) * height / 640;
            int src_idx = (src_y * width + src_x) * 3;
            
            input_tensor_values[i * 3] = image_data[src_idx] / 255.0f;     // R
            input_tensor_values[i * 3 + 1] = image_data[src_idx + 1] / 255.0f; // G
            input_tensor_values[i * 3 + 2] = image_data[src_idx + 2] / 255.0f; // B
        }
        
        std::vector<int64_t> input_shape = {1, 3, 640, 640};
        Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
            *memory_info_,
            input_tensor_values.data(),
            input_tensor_values.size(),
            input_shape.data(),
            input_shape.size()
        );
        
        const char* input_names[] = {input_name_.c_str()};
        const char* output_names[] = {output_name_.c_str()};
        
        auto output_tensor = session_->Run(
            Ort::RunOptions{nullptr},
            input_names,
            &input_tensor,
            1,
            output_names,
            1
        );
        
        float* output_data = output_tensor.front().GetTensorMutableData<float>();
        
        detections = parseOutput(output_data, width, height);
        
    } catch (const Ort::Exception& e) {
        std::cerr << "[SimpleInference] Inference error: " << e.what() << std::endl;
    }
    
    return detections;
}

std::vector<Detection> SimpleInference::parseOutput(
    float* output_data,
    int img_width,
    int img_height
) {
    std::vector<Detection> detections;
    
    // Format YOLO: [batch, 8400, 85] (85 = 4 bbox + 1 conf + 80 classes)
    const int num_detections = 8400;
    const int num_classes = 80;
    
    for (int i = 0; i < num_detections; ++i) {
        float* det = output_data + i * (4 + 1 + num_classes);
        
        float x = det[0];
        float y = det[1];
        float w = det[2];
        float h = det[3];
        float conf = det[4];
        
        if (conf < conf_threshold_) {
            continue;
        }
        
        // Trouver la classe avec la probabilité max
        int max_class_id = 0;
        float max_class_prob = det[5];
        
        for (int c = 1; c < num_classes; ++c) {
            if (det[5 + c] > max_class_prob) {
                max_class_prob = det[5 + c];
                max_class_id = c;
            }
        }
        
        float final_conf = conf * max_class_prob;
        if (final_conf < conf_threshold_) {
            continue;
        }
        
        Detection d;
        d.x = x - w / 2;
        d.y = y - h / 2;
        d.width = w;
        d.height = h;
        d.confidence = final_conf;
        d.class_id = max_class_id;
        d.class_name = "class_" + std::to_string(max_class_id);
        
        detections.push_back(d);
    }
    
    return detections;
}

} // namespace fall_detection
