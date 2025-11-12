#!/bin/bash

# 定时任务模拟运行脚本
# 用于快速启动和管理定时任务模拟

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 检查 Python 环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未找到"
        exit 1
    fi

    # 检查是否在正确的项目目录中
    if [[ ! -f "$PROJECT_DIR/src/scheduler/tasks.py" ]]; then
        log_error "请在 suagent-tasks 项目目录中运行此脚本"
        exit 1
    fi
}

# 验证配置
validate_config() {
    log_info "验证定时任务配置..."
    cd "$PROJECT_DIR"
    python3 "$SCRIPT_DIR/simulate_scheduler.py" validate
}

# 模拟每日同步任务
simulate_daily_sync() {
    log_info "模拟每日用户记忆同步任务..."
    cd "$PROJECT_DIR"

    local start_date="$1"
    if [[ -n "$start_date" ]]; then
        python3 "$SCRIPT_DIR/simulate_scheduler.py" sync_daily --start-date "$start_date" --dry-run
    else
        python3 "$SCRIPT_DIR/simulate_scheduler.py" sync_daily --dry-run
    fi
}

# 执行每日同步任务
execute_daily_sync() {
    log_warn "实际执行每日用户记忆同步任务..."
    cd "$PROJECT_DIR"

    local start_date="$1"
    if [[ -n "$start_date" ]]; then
        python3 "$SCRIPT_DIR/simulate_scheduler.py" sync_daily --start-date "$start_date" --execute
    else
        python3 "$SCRIPT_DIR/simulate_scheduler.py" sync_daily --execute
    fi
}

# 模拟单个用户同步
simulate_user_sync() {
    local user_id="$1"
    if [[ -z "$user_id" ]]; then
        log_error "用户ID不能为空"
        exit 1
    fi

    log_info "模拟用户 $user_id 的记忆同步任务..."
    cd "$PROJECT_DIR"
    python3 "$SCRIPT_DIR/simulate_scheduler.py" sync_user "$user_id" --dry-run
}

# 执行单个用户同步
execute_user_sync() {
    local user_id="$1"
    if [[ -z "$user_id" ]]; then
        log_error "用户ID不能为空"
        exit 1
    fi

    log_warn "实际执行用户 $user_id 的记忆同步任务..."
    cd "$PROJECT_DIR"
    python3 "$SCRIPT_DIR/simulate_scheduler.py" sync_user "$user_id" --execute
}

# 模拟存储监控
simulate_monitoring() {
    log_info "模拟存储使用监控任务..."
    cd "$PROJECT_DIR"
    python3 "$SCRIPT_DIR/simulate_scheduler.py" monitor --dry-run
}

# 执行存储监控
execute_monitoring() {
    log_warn "实际执行存储使用监控任务..."
    cd "$PROJECT_DIR"
    python3 "$SCRIPT_DIR/simulate_scheduler.py" monitor --execute
}

# 模拟清理任务
simulate_cleanup() {
    local days="${1:-30}"
    log_info "模拟清理 $days 天前的旧日志任务..."
    cd "$PROJECT_DIR"
    python3 "$SCRIPT_DIR/simulate_scheduler.py" cleanup --days "$days" --dry-run
}

# 执行清理任务
execute_cleanup() {
    local days="${1:-30}"
    log_warn "实际执行清理 $days 天前的旧日志任务..."
    cd "$PROJECT_DIR"
    python3 "$SCRIPT_DIR/simulate_scheduler.py" cleanup --days "$days" --execute
}

# 间隔模拟任务
simulate_interval() {
    local task="$1"
    local interval="${2:-60}"

    if [[ -z "$task" ]]; then
        log_error "任务名称不能为空"
        show_usage
        exit 1
    fi

    log_info "启动间隔模拟: 任务=$task, 间隔=${interval}秒"
    log_info "按 Ctrl+C 停止模拟"

    cd "$PROJECT_DIR"
    python3 "$SCRIPT_DIR/simulate_scheduler.py" simulate "$task" --interval "$interval" --dry-run
}

# 快速测试所有任务
quick_test() {
    log_info "执行快速测试 - 模拟所有主要任务..."

    echo
    log_info "1/4 验证配置..."
    validate_config

    echo
    log_info "2/4 模拟每日同步..."
    simulate_daily_sync

    echo
    log_info "3/4 模拟存储监控..."
    simulate_monitoring

    echo
    log_info "4/4 模拟清理任务..."
    simulate_cleanup 7

    echo
    log_info "快速测试完成！"
}

# 完整测试（包含实际执行）
full_test() {
    log_warn "执行完整测试 - 包含实际任务执行..."
    log_warn "这将实际执行任务，请确认是否继续？"
    read -p "继续执行? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "已取消完整测试"
        exit 0
    fi

    echo
    log_info "1/4 验证配置..."
    validate_config

    echo
    log_warn "2/4 执行每日同步..."
    execute_daily_sync

    echo
    log_warn "3/4 执行存储监控..."
    execute_monitoring

    echo
    log_warn "4/4 执行清理任务（清理7天前的日志）..."
    execute_cleanup 7

    echo
    log_info "完整测试完成！"
}

# 显示帮助信息
show_usage() {
    echo "定时任务模拟运行脚本"
    echo
    echo "用法: $0 {command} [options]"
    echo
    echo "命令:"
    echo "  validate                        验证定时任务配置"
    echo "  simulate-daily [date]          模拟每日同步任务"
    echo "  execute-daily [date]           实际执行每日同步任务"
    echo "  simulate-user <user_id>        模拟指定用户同步"
    echo "  execute-user <user_id>         实际执行指定用户同步"
    echo "  simulate-monitor               模拟存储监控任务"
    echo "  execute-monitor                实际执行存储监控任务"
    echo "  simulate-cleanup [days]        模拟清理任务"
    echo "  execute-cleanup [days]         实际执行清理任务"
    echo "  simulate-interval <task> <sec> 间隔模拟任务"
    echo "  quick-test                     快速测试（模拟模式）"
    echo "  full-test                      完整测试（实际执行）"
    echo "  help                           显示此帮助信息"
    echo
    echo "参数说明:"
    echo "  date       日期格式 YYYY-MM-DD（可选，默认为昨天）"
    echo "  user_id    用户ID"
    echo "  days       保留天数（默认为30）"
    echo "  task       任务名称: sync_daily, monitor, cleanup"
    echo "  sec        间隔秒数（默认为60）"
    echo
    echo "示例:"
    echo "  $0 validate                           # 验证配置"
    echo "  $0 simulate-daily                     # 模拟每日同步"
    echo "  $0 execute-daily 2024-01-15           # 执行指定日期的同步"
    echo "  $0 simulate-user user123              # 模拟用户同步"
    echo "  $0 simulate-monitor                   # 模拟存储监控"
    echo "  $0 simulate-cleanup 7                 # 模拟清理7天前的日志"
    echo "  $0 simulate-interval monitor 30       # 每30秒模拟一次监控任务"
    echo "  $0 quick-test                         # 快速测试"
    echo
    echo "注意:"
    echo "  - 模拟模式（simulate-*）不会实际修改数据"
    echo "  - 执行模式（execute-*）会实际操作数据库和存储"
    echo "  - full-test 需要确认才会执行实际任务"
}

# 主函数
main() {
    # 检查 Python 环境
    check_python

    case "${1:-help}" in
        validate)
            validate_config
            ;;
        simulate-daily)
            simulate_daily_sync "$2"
            ;;
        execute-daily)
            execute_daily_sync "$2"
            ;;
        simulate-user)
            simulate_user_sync "$2"
            ;;
        execute-user)
            execute_user_sync "$2"
            ;;
        simulate-monitor)
            simulate_monitoring
            ;;
        execute-monitor)
            execute_monitoring
            ;;
        simulate-cleanup)
            simulate_cleanup "$2"
            ;;
        execute-cleanup)
            execute_cleanup "$2"
            ;;
        simulate-interval)
            simulate_interval "$2" "$3"
            ;;
        quick-test)
            quick_test
            ;;
        full-test)
            full_test
            ;;
        help|--help|-h)
            show_usage
            ;;
        *)
            log_error "未知命令: $1"
            echo
            show_usage
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"