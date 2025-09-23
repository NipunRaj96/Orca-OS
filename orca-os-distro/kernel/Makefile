# Orca OS Kernel Module and C++ Middleware Makefile
# High-performance AI integration for Linux kernel

# Compiler and flags
CXX = g++
CC = gcc
KERNEL_DIR = /lib/modules/$(shell uname -r)/build

# C++ flags for high performance
CXXFLAGS = -std=c++17 -O3 -march=native -mtune=native -flto -fPIC
CXXFLAGS += -Wall -Wextra -Werror -Wno-unused-parameter
CXXFLAGS += -DNDEBUG -DORCA_AI_PERFORMANCE

# C flags for kernel module
CFLAGS = -O2 -Wall -Wextra -Werror -Wno-unused-parameter
CFLAGS += -D__KERNEL__ -DMODULE -DKBUILD_MODNAME=\"orca_ai\"

# Include directories
INCLUDES = -I. -I/opt/orca-os/include -I/usr/include

# Library paths and libraries
LIBPATHS = -L/opt/orca-os/lib -L/usr/lib/x86_64-linux-gnu
LIBS = -lpthread -ldl -lrt -lcurl -ljsoncpp

# Source files
KERNEL_SOURCES = orca-kernel-module.c
CPP_SOURCES = orca-ai-middleware.cpp orca_ai_llm.cpp orca_ai_scheduler.cpp \
              orca_ai_memory.cpp orca_ai_network.cpp

# Object files
KERNEL_OBJECTS = $(KERNEL_SOURCES:.c=.o)
CPP_OBJECTS = $(CPP_SOURCES:.cpp=.o)

# Targets
KERNEL_MODULE = orca_ai.ko
MIDDLEWARE_LIB = liborca_ai_middleware.so
MIDDLEWARE_BIN = orca_ai_middleware

# Default target
all: $(KERNEL_MODULE) $(MIDDLEWARE_LIB) $(MIDDLEWARE_BIN)

# Kernel module
$(KERNEL_MODULE): $(KERNEL_OBJECTS)
	@echo "Building kernel module: $@"
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) modules
	@echo "✅ Kernel module built successfully"

# C++ middleware library
$(MIDDLEWARE_LIB): $(CPP_OBJECTS)
	@echo "Building C++ middleware library: $@"
	$(CXX) $(CXXFLAGS) -shared -o $@ $(CPP_OBJECTS) $(LIBPATHS) $(LIBS)
	@echo "✅ C++ middleware library built successfully"

# C++ middleware binary
$(MIDDLEWARE_BIN): $(CPP_OBJECTS) main.cpp
	@echo "Building C++ middleware binary: $@"
	$(CXX) $(CXXFLAGS) -o $@ main.cpp $(CPP_OBJECTS) $(LIBPATHS) $(LIBS)
	@echo "✅ C++ middleware binary built successfully"

# Compile C++ objects
%.o: %.cpp
	@echo "Compiling C++: $<"
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

# Compile C objects
%.o: %.c
	@echo "Compiling C: $<"
	$(CC) $(CFLAGS) $(INCLUDES) -c $< -o $@

# Install targets
install: all
	@echo "Installing Orca AI kernel components..."
	sudo cp $(KERNEL_MODULE) /lib/modules/$(shell uname -r)/extra/
	sudo cp $(MIDDLEWARE_LIB) /usr/lib/
	sudo cp $(MIDDLEWARE_BIN) /usr/local/bin/
	sudo depmod -a
	@echo "✅ Installation complete"

# Load kernel module
load: $(KERNEL_MODULE)
	@echo "Loading Orca AI kernel module..."
	sudo insmod $(KERNEL_MODULE)
	@echo "✅ Kernel module loaded"

# Unload kernel module
unload:
	@echo "Unloading Orca AI kernel module..."
	sudo rmmod orca_ai
	@echo "✅ Kernel module unloaded"

# Test kernel module
test-kernel: load
	@echo "Testing kernel module..."
	cat /proc/orca_ai
	@echo "✅ Kernel module test complete"

# Test C++ middleware
test-middleware: $(MIDDLEWARE_BIN)
	@echo "Testing C++ middleware..."
	./$(MIDDLEWARE_BIN) --test
	@echo "✅ C++ middleware test complete"

# Performance benchmark
benchmark: $(MIDDLEWARE_BIN)
	@echo "Running performance benchmark..."
	./$(MIDDLEWARE_BIN) --benchmark
	@echo "✅ Benchmark complete"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f $(KERNEL_OBJECTS) $(CPP_OBJECTS)
	rm -f $(KERNEL_MODULE) $(MIDDLEWARE_LIB) $(MIDDLEWARE_BIN)
	rm -f *.mod.c *.mod *.o *.ko *.so
	rm -f Module.symvers Module.markers modules.order
	rm -rf .tmp_versions
	@echo "✅ Clean complete"

# Clean kernel module build
clean-kernel:
	@echo "Cleaning kernel module..."
	$(MAKE) -C $(KERNEL_DIR) M=$(PWD) clean
	@echo "✅ Kernel module clean complete"

# Debug build
debug: CXXFLAGS += -g -DDEBUG -O0
debug: CFLAGS += -g -DDEBUG -O0
debug: clean all

# Release build
release: CXXFLAGS += -DNDEBUG -O3 -march=native
release: CFLAGS += -DNDEBUG -O3
release: clean all

# Help target
help:
	@echo "Orca OS Kernel Module and C++ Middleware Build System"
	@echo "======================================================"
	@echo ""
	@echo "Available targets:"
	@echo "  all              - Build everything (default)"
	@echo "  $(KERNEL_MODULE)     - Build kernel module only"
	@echo "  $(MIDDLEWARE_LIB)    - Build C++ middleware library only"
	@echo "  $(MIDDLEWARE_BIN)    - Build C++ middleware binary only"
	@echo "  install          - Install all components"
	@echo "  load             - Load kernel module"
	@echo "  unload           - Unload kernel module"
	@echo "  test-kernel      - Test kernel module"
	@echo "  test-middleware  - Test C++ middleware"
	@echo "  benchmark        - Run performance benchmark"
	@echo "  clean            - Clean build artifacts"
	@echo "  clean-kernel     - Clean kernel module only"
	@echo "  debug            - Build with debug symbols"
	@echo "  release          - Build optimized release"
	@echo "  help             - Show this help"
	@echo ""
	@echo "Examples:"
	@echo "  make all                    # Build everything"
	@echo "  make install                # Build and install"
	@echo "  make load && make test      # Load and test"
	@echo "  make benchmark              # Run performance test"
	@echo "  make clean && make release  # Clean and build optimized"

# Phony targets
.PHONY: all install load unload test-kernel test-middleware benchmark clean clean-kernel debug release help
