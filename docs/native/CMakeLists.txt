cmake_minimum_required(VERSION 3.16)
project(sentinel_onnx LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

# Optionnel : accélération ONNX Runtime
# cmake -DONNXRUNTIME_ROOT=/path/to/onnxruntime ..
option(BUILD_ONNX_INFER "Build ONNX infer shared lib" OFF)

if(BUILD_ONNX_INFER)
  if(NOT ONNXRUNTIME_ROOT)
    message(FATAL_ERROR "Set -DONNXRUNTIME_ROOT=...")
  endif()
  include_directories(${ONNXRUNTIME_ROOT}/include include)
  link_directories(${ONNXRUNTIME_ROOT}/lib)
  add_library(onnx_infer SHARED src/onnx_infer.cpp)
  target_link_libraries(onnx_infer onnxruntime)
  install(TARGETS onnx_infer DESTINATION lib)
endif()

message(STATUS "SentinelAI native: BUILD_ONNX_INFER=${BUILD_ONNX_INFER}")
