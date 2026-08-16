cmake_minimum_required(VERSION 3.16)
project(FallDetectionBackend VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

if(MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra)
endif()

# ONNX Runtime — cross-platform (env, -D, or common paths)
if(NOT ONNXRUNTIME_ROOT)
    if(DEFINED ENV{ONNXRUNTIME_ROOT} AND NOT "$ENV{ONNXRUNTIME_ROOT}" STREQUAL "")
        set(ONNXRUNTIME_ROOT "$ENV{ONNXRUNTIME_ROOT}")
    endif()
endif()
if(NOT ONNXRUNTIME_ROOT)
    set(_ONNX_CANDIDATES
        "${CMAKE_SOURCE_DIR}/../third_party/onnxruntime"
        "${CMAKE_SOURCE_DIR}/third_party/onnxruntime"
        "/usr/local/onnxruntime"
        "/opt/onnxruntime"
        "$ENV{HOME}/onnxruntime"
        "C:/fall_detection_deps/onnxruntime"
        "C:/onnxruntime"
    )
    foreach(_cand IN LISTS _ONNX_CANDIDATES)
        if(EXISTS "${_cand}/include" AND (EXISTS "${_cand}/lib" OR EXISTS "${_cand}/lib64"))
            set(ONNXRUNTIME_ROOT "${_cand}")
            break()
        endif()
    endforeach()
endif()
set(ONNXRUNTIME_ROOT "${ONNXRUNTIME_ROOT}" CACHE PATH "Path to ONNX Runtime root")
if(NOT ONNXRUNTIME_ROOT OR NOT EXISTS "${ONNXRUNTIME_ROOT}/include")
    message(FATAL_ERROR "ONNX Runtime not found. Set -DONNXRUNTIME_ROOT=/path or export ONNXRUNTIME_ROOT")
endif()
message(STATUS "ONNX Runtime: ${ONNXRUNTIME_ROOT}")
include_directories(${ONNXRUNTIME_ROOT}/include)
if(EXISTS "${ONNXRUNTIME_ROOT}/lib64")
    link_directories(${ONNXRUNTIME_ROOT}/lib64)
else()
    link_directories(${ONNXRUNTIME_ROOT}/lib)
endif()
include_directories(${CMAKE_SOURCE_DIR}/include)
set(ONNXRUNTIME_LIBS onnxruntime)
add_executable(fall_detection_backend
    src/main.cpp
    src/onnx_engine/SimpleInference.cpp
    src/network/TcpServer.cpp
)
target_link_libraries(fall_detection_backend ${ONNXRUNTIME_LIBS})
if(UNIX AND NOT APPLE)
    find_package(Threads REQUIRED)
    target_link_libraries(fall_detection_backend Threads::Threads ${CMAKE_DL_LIBS})
endif()
install(TARGETS fall_detection_backend RUNTIME DESTINATION bin)
