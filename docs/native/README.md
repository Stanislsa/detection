# Module natif C++ (optionnel)

```bash
mkdir -p build && cd build
cmake .. -DBUILD_ONNX_INFER=ON -DONNXRUNTIME_ROOT=/usr/local
make -j
```

Sans compilation, le backend utilise YOLO / OpenVINO / MediaPipe en Python.
