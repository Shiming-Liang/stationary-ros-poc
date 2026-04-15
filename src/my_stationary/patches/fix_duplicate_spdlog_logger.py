#!/usr/bin/env python3
"""
Fix: pre-register spdlog loggers in TrossenArmHardwareInterface::on_configure()
before constructing TrossenArmDriver to prevent a race between spdlog::get() and
spdlog::stdout_color_mt() when multiple hardware interfaces are configured in the
same ros2_control_node process.

See: https://github.com/TrossenRobotics/trossen_arm/issues/196
"""
import sys

path = sys.argv[1]
with open(path, 'r') as f:
    content = f.read()

# 1. Add spdlog includes after trossen_arm_hardware/interface.hpp
old = '#include "trossen_arm_hardware/interface.hpp"'
new = (
    '#include "trossen_arm_hardware/interface.hpp"\n'
    '#include "spdlog/sinks/stdout_color_sinks.h"\n'
    '#include "spdlog/spdlog.h"'
)
assert old in content, "include marker not found"
content = content.replace(old, new, 1)

# 2. Pre-register loggers in on_configure before constructing TrossenArmDriver
old = (
    '  RCLCPP_INFO(get_logger(), "Configuring the Trossen Arm Driver...");\n'
    '  try {\n'
    '    arm_driver_ = std::make_unique<TrossenArmDriver>();'
)
new = (
    '  RCLCPP_INFO(get_logger(), "Configuring the Trossen Arm Driver...");\n'
    '\n'
    '  // Pre-register spdlog loggers before constructing TrossenArmDriver to avoid\n'
    '  // "logger with name \'trossen_arm_driver\' already exists" when multiple\n'
    '  // TrossenArmHardwareInterface instances are configured in the same process.\n'
    '  // Logger::Logger() uses spdlog::get(name) then spdlog::stdout_color_mt(name),\n'
    '  // but these are not atomic - two threads can both pass the get() check and\n'
    '  // then race to create the logger. Pre-registering here eliminates the race.\n'
    '  {\n'
    '    auto sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();\n'
    '    for (const auto & name : {\n'
    '        TrossenArmDriver::get_default_logger_name(),\n'
    '        TrossenArmDriver::get_logger_name(robot_model_, driver_ip_address_)})\n'
    '    {\n'
    '      if (!spdlog::get(name)) {\n'
    '        spdlog::register_logger(std::make_shared<spdlog::logger>(name, sink));\n'
    '      }\n'
    '    }\n'
    '  }\n'
    '\n'
    '  try {\n'
    '    arm_driver_ = std::make_unique<TrossenArmDriver>();'
)
assert old in content, "on_configure marker not found"
content = content.replace(old, new, 1)

# 3. Drop loggers in on_cleanup so they can be re-registered on error recovery
old = (
    '  robot_output_ = trossen_arm::RobotOutput();\n'
    '  arm_driver_.reset();'
)
new = (
    '  robot_output_ = trossen_arm::RobotOutput();\n'
    '  // Drop loggers from spdlog registry so on_configure() can re-register them\n'
    '  // if called again after error recovery.\n'
    '  spdlog::drop(TrossenArmDriver::get_logger_name(robot_model_, driver_ip_address_));\n'
    '  spdlog::drop(TrossenArmDriver::get_default_logger_name());\n'
    '  arm_driver_.reset();'
)
assert old in content, "on_cleanup marker not found"
content = content.replace(old, new, 1)

with open(path, 'w') as f:
    f.write(content)

print("fix_duplicate_spdlog_logger: patch applied successfully.")
