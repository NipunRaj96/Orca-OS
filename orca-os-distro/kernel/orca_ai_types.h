/*
 * Orca AI Types - C++ Data Structures for High-Performance AI Integration
 */

#ifndef ORCA_AI_TYPES_H
#define ORCA_AI_TYPES_H

#include <chrono>
#include <string>
#include <vector>
#include <unordered_map>
#include <atomic>
#include <mutex>

namespace orca {
namespace ai {

// AI Request Types
enum class AIRequestType {
    PROCESS_ANALYSIS,
    SYSTEM_OPTIMIZATION,
    PREDICTIVE_ANALYSIS,
    RESOURCE_MANAGEMENT,
    NETWORK_OPTIMIZATION,
    SECURITY_ANALYSIS
};

// Process Context
struct ProcessContext {
    pid_t pid;
    std::string name;
    double cpu_usage;
    size_t memory_usage;
    int priority;
    std::string status;
    std::chrono::system_clock::time_point start_time;
    std::chrono::system_clock::time_point last_analyzed;
    std::string ai_insight;
    std::vector<std::string> recommendations;
    int ai_importance;  // 1=low, 2=medium, 3=high
};

// AI Request
struct AIRequest {
    uint64_t request_id;
    AIRequestType type;
    pid_t pid;
    ProcessContext context;
    std::string user_query;
    std::chrono::system_clock::time_point timestamp;
    std::unordered_map<std::string, std::string> parameters;
};

// AI Response
struct AIResponse {
    uint64_t request_id;
    bool success;
    std::string error;
    std::string insights;
    std::vector<std::string> recommendations;
    std::chrono::system_clock::time_point timestamp;
    uint64_t latency_us;
    bool optimization_applied;
    std::string prediction;
    std::string resource_allocation;
    std::string plan;
};

// System State
struct SystemState {
    double cpu_usage;
    size_t memory_usage;
    size_t disk_usage;
    size_t network_usage;
    int process_count;
    std::chrono::system_clock::time_point timestamp;
    std::vector<ProcessContext> processes;
};

// Optimization Plan
struct OptimizationPlan {
    std::vector<std::string> cpu_optimizations;
    std::vector<std::string> memory_optimizations;
    std::vector<std::string> disk_optimizations;
    std::vector<std::string> network_optimizations;
    int priority;
    double expected_improvement;
    std::string description;
};

// Resource Allocation
struct ResourceAllocation {
    size_t memory_limit;
    int cpu_affinity;
    int priority;
    std::vector<std::string> optimizations;
    double confidence;
};

// Prediction Result
struct PredictionResult {
    std::string prediction;
    double confidence;
    std::vector<std::string> recommendations;
    std::chrono::system_clock::time_point predicted_time;
    std::string risk_level;
};

// Performance Metrics
struct PerformanceMetrics {
    uint64_t requests_processed;
    uint64_t total_latency_us;
    uint64_t ai_insights_generated;
    uint64_t average_latency_us;
    size_t processes_monitored;
    double cpu_efficiency;
    double memory_efficiency;
    double prediction_accuracy;
};

// LLM Engine Interface
class LLMEngine {
public:
    virtual ~LLMEngine() = default;
    virtual bool initialize() = 0;
    virtual std::string generate_insight(const std::string& prompt) = 0;
    virtual PredictionResult predict_system_behavior(const std::vector<SystemState>& history) = 0;
    virtual std::vector<std::string> generate_recommendations(const ProcessContext& context) = 0;
};

// AI Scheduler Interface
class AIScheduler {
public:
    virtual ~AIScheduler() = default;
    virtual bool initialize() = 0;
    virtual OptimizationPlan create_optimization_plan(const SystemState& state) = 0;
    virtual bool apply_optimization(const std::string& optimization) = 0;
    virtual void optimize_process_priority(pid_t pid, int new_priority) = 0;
};

// Memory Manager Interface
class MemoryManager {
public:
    virtual ~MemoryManager() = default;
    virtual bool initialize() = 0;
    virtual ResourceAllocation optimize_allocation(const ProcessContext& context) = 0;
    virtual bool apply_allocation(const ResourceAllocation& allocation) = 0;
    virtual void cleanup_memory() = 0;
};

// Network Optimizer Interface
class NetworkOptimizer {
public:
    virtual ~NetworkOptimizer() = default;
    virtual bool initialize() = 0;
    virtual void optimize_network_settings() = 0;
    virtual void monitor_network_usage() = 0;
    virtual std::vector<std::string> get_network_recommendations() = 0;
};

} // namespace ai
} // namespace orca

#endif // ORCA_AI_TYPES_H
