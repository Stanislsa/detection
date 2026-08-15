#pragma once

#include <vector>
#include <string>
#include <cstdint>
#include <memory>

#include <onnxruntime_cxx_api.h>

namespace fall_detection {

struct Detection {
    float x, y, width, height;
    float confidence;
    int class_id;
    std::string class_name;
};

class SimpleInference {
public:
    SimpleInference(const std::string& model_path);
    ~SimpleInference();
    
    bool load();
    
    std::vector<Detection> infer(
        const uint8_t* image_data,
        int width,
        int height
    );
    
    void setConfidenceThreshold(float threshold) { conf_threshold_ = threshold; }
    bool isReady() const { return session_ != nullptr; }

private:
    std::string model_path_;
    std::unique_ptr<Ort::Env> env_;
    std::unique_ptr<Ort::Session> session_;
    std::unique_ptr<Ort::MemoryInfo> memory_info_;
    
    float conf_threshold_ = 0.5f;
    
    std::string input_name_;
    std::string output_name_;
    
    std::vector<Detection> parseOutput(
        float* output_data,
        int img_width,
        int img_height
    );
};

} // namespace fall_detection
