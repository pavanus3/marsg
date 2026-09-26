import json

blackwell_architecture = {
    "Project": "marsg",
    "Architecture": "NVIDIA Blackwell",
    "Description": "Block diagram of the Blackwell architecture including SM, Tensor Core, ALU, and Compiler Instruction mappings.",
    "Top_Level_Blocks": [
        {
            "Block_Name": "GPU_Global",
            "Sub_Blocks": [
                {
                    "Name": "Global Memory",
                    "Details": "HBM3e Memory, High Bandwidth Memory",
                    "Compiler_Mapping": "Global memory access via LD.GLOBAL, ST.GLOBAL"
                },
                {
                    "Name": "L2 Cache",
                    "Details": "Unified L2 Cache across the GPU",
                    "Compiler_Mapping": "Cached via global memory instructions"
                },
                {
                    "Name": "Interconnect",
                    "Details": "NVLink 5.0, PCIe Gen6",
                    "Compiler_Mapping": "Multi-GPU and CPU-GPU copy instructions"
                },
                {
                    "Name": "TMA (Tensor Memory Accelerator)",
                    "Details": "Hardware block for asynchronous data movement between global memory and shared memory",
                    "Compiler_Mapping": "cp.async.bulk, mbarrier (Triton utilizes this heavily)"
                },
                {
                    "Name": "CBA (Cluster-Based Architecture)",
                    "Details": "Thread Block Clusters for localized synchronization and fast data exchange",
                    "Compiler_Mapping": "mapa (multicast), barrier.cluster"
                }
            ]
        },
        {
            "Block_Name": "GPC (Graphics Processing Cluster)",
            "Details": "Multiple GPCs per GPU, containing multiple TPCs",
            "Sub_Blocks": [
                {
                    "Block_Name": "TPC (Texture Processing Cluster)",
                    "Details": "Contains SMs, Ray Tracing Cores, and Texture Units",
                    "Sub_Blocks": [
                        {
                            "Name": "RT Core (4th Gen)",
                            "Details": "Ray-Tracing & Opacity Micromap Engine",
                            "Compiler_Mapping": "Ray Tracing API instructions"
                        },
                        {
                            "Block_Name": "SM (Streaming Multiprocessor)",
                            "Details": "The core processing unit for compute",
                            "Memory_and_Control": [
                                {
                                    "Name": "Warp Schedulers & Dispatch Units",
                                    "Details": "Schedules thread warps and dispatches instructions",
                                    "Compiler_Mapping": "Controls instruction issue rates, thread level execution (tcgen05)"
                                },
                                {
                                    "Name": "Register File (RF)",
                                    "Details": "256 KB capacity per SM",
                                    "Compiler_Mapping": "R0-R255 registers in PTX/SASS"
                                },
                                {
                                    "Name": "L1 Cache / Shared Memory (SMEM)",
                                    "Details": "128 KB - 228 KB Configurable",
                                    "Compiler_Mapping": "LD.SHARED, ST.SHARED, wgmma operands"
                                },
                                {
                                    "Name": "TMEM (Tensor Memory)",
                                    "Details": "256 KB dedicated memory for Tensor Core intermediates (New in Blackwell). Reduces register pressure.",
                                    "Compiler_Mapping": "tcgen05.commit, explicit TMEM addressing"
                                }
                            ],
                            "Processing_Partitions": {
                                "Details": "4 Partitions per SM, each executing instructions independently",
                                "Sub_Blocks": [
                                    {
                                        "Name": "CUDA Cores (Unified ALU)",
                                        "Quantity": "32 per Partition (128 per SM)",
                                        "Capabilities": "Unified FP32 and INT32 execution datapaths",
                                        "Compiler_Mapping": {
                                            "FP32": "FADD, FMUL, FFMA (Floating Point Math)",
                                            "INT32": "IADD, IMUL, LOP3 (Integer Math and Logic)"
                                        }
                                    },
                                    {
                                        "Name": "Tensor Cores (5th Gen)",
                                        "Quantity": "1 per Partition (4 per SM)",
                                        "Capabilities": "Transformer Engine 2.0, support for NVFP4, FP6, FP8, BF16, FP16, TF32, FP64",
                                        "Compiler_Mapping": "tcgen05.mma (Thread-level tensor ops), wgmma.mma_async (Warp-group mma)"
                                    },
                                    {
                                        "Name": "LD/ST Units (Load/Store)",
                                        "Quantity": "Multiple per Partition",
                                        "Capabilities": "Handles memory addresses and data transfers",
                                        "Compiler_Mapping": "LD, ST, ATOM, RED (Atomic and Reduction ops)"
                                    },
                                    {
                                        "Name": "SFU (Special Function Units)",
                                        "Quantity": "Multiple per Partition",
                                        "Capabilities": "Calculates transcendentals (sine, cosine, exponential, etc.)",
                                        "Compiler_Mapping": "MUFU (Sine, Cosine, Ex2, Lg2, Rcp, Rsq)"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    ],
    "Ecosystem_Integration": {
        "Triton": "Compiles Python directly to PTX, leveraging TMA (cp.async.bulk) and WGMMA/tcgen05 instructions for Blackwell SMs.",
        "vLLM": "Leverages 5th-gen Tensor Cores and FP4/FP8 capabilities for highly efficient KV cache and LLM decoding.",
        "SCALE-Sim": "Simulates the systolic array configurations internally used by the 5th-Gen Tensor Cores.",
        "Modular (Mojo)": "Uses MAX engine and MLIR dialects to generate highly optimized SASS targeting unified CUDA cores and TMEM."
    }
}

with open("/config/Desktop/BuildWithGemini/marsg/blackwell_block_diagram.json", "w") as f:
    json.dump(blackwell_architecture, f, indent=4)
print("JSON created successfully.")
