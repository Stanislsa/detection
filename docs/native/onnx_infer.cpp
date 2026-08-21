// Stub ONNX infer — activer avec -DBUILD_ONNX_INFER=ON
// Remplacer par intégration ONNX Runtime réelle si besoin.
#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __attribute__((visibility("default")))
#endif

extern "C" EXPORT int sentinel_onnx_version() { return 1; }
extern "C" EXPORT int sentinel_onnx_available() { return 0; }
