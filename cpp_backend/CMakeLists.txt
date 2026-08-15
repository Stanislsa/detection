cmake_minimum_required(VERSION 3.16)
project(FallDetectionBackend VERSION 1.0.0 LANGUAGES CXX)

# Configuration C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Configuration de sortie
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# Flags de compilation
if(MSVC)
    add_compile_options(/W4)
else()
    add_compile_options(-Wall -Wextra)
endif()

# ONNX Runtime (seule dependance requise)
set(ONNXRUNTIME_ROOT "C:/fall_detection_deps/onnxruntime" CACHE PATH "Path to ONNX Runtime root directory")
if(ONNXRUNTIME_ROOT)
    include_directories(${ONNXRUNTIME_ROOT}/include)
    link_directories(${ONNXRUNTIME_ROOT}/lib)
else()
    message(FATAL_ERROR "ONNXRUNTIME_ROOT not set. Please set: -DONNXRUNTIME_ROOT=path/to/onnxruntime")
endif()

# Inclusions globales
include_directories(${CMAKE_SOURCE_DIR}/include)

# Bibliothèques ONNX Runtime
if(WIN32)
    set(ONNXRUNTIME_LIBS onnxruntime)
elseif(UNIX)
    set(ONNXRUNTIME_LIBS onnxruntime)
endif()

# Exécutable principal minimaliste
add_executable(fall_detection_backend
    src/main.cpp
    src/onnx_engine/SimpleInference.cpp
    src/network/TcpServer.cpp
)

target_link_libraries(fall_detection_backend
    ${ONNXRUNTIME_LIBS}
)

if(WIN32)
    target_link_libraries(fall_detection_backend ws2_32)
endif()

# Installation
install(TARGETS fall_detection_backend
    RUNTIME DESTINATION bin
)

# Affichage du résumé
message(STATUS "")
message(STATUS "=== Fall Detection Backend (Minimal) ===")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "ONNX Runtime: ${ONNXRUNTIME_ROOT}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "========================================")
