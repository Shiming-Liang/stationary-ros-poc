FROM ros:jazzy-ros-base

ENV DEBIAN_FRONTEND=noninteractive
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

RUN apt update && apt install -y git ros-jazzy-rmw-cyclonedds-cpp

# Build Trossen dependencies
COPY src/my_stationary/patches/ /patches/
RUN apt update && \
    mkdir -p /trossen_ws/src && \
    git clone --branch v1.9.1 --depth 1 https://github.com/TrossenRobotics/trossen_arm.git /trossen_ws/src/trossen_arm && \
    git clone --branch main --depth 1 https://github.com/pzal/trossen_arm_description.git /trossen_ws/src/trossen_arm_description && \
    # Use a fork from traclabs because there's a necessary build fix there
    git clone --branch hotfix/rolling-error-fixes --depth 1 https://github.com/traclabs/trossen_arm_ros /trossen_ws/src/trossen_arm_ros && \
    # Fix: pre-register spdlog loggers before constructing TrossenArmDriver to prevent
    # a TOCTOU race between spdlog::get() and spdlog::stdout_color_mt() when multiple
    # hardware interfaces are configured concurrently in the same ros2_control_node process
    python3 /patches/fix_duplicate_spdlog_logger.py /trossen_ws/src/trossen_arm_ros/trossen_arm_hardware/src/interface.cpp && \
    cd /trossen_ws && \
    rosdep install --from-paths src --ignore-src -r -y --rosdistro jazzy && \
    bash -c "source /opt/ros/jazzy/setup.bash && colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release"

# Build the stationary-ros-poc workspace
COPY src/ /workspace/stationary-ros-poc/src/
RUN cd /workspace/stationary-ros-poc && \
    bash -c "source /opt/ros/jazzy/setup.bash && source /trossen_ws/install/setup.bash && \
             colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release"

RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc && \
    echo "source /trossen_ws/install/setup.bash" >> /root/.bashrc && \
    echo "source /workspace/stationary-ros-poc/install/setup.bash" >> /root/.bashrc

WORKDIR /workspace/stationary-ros-poc
