#!/bin/bash

# Memory Sync Scheduler 启动脚本
# 用于启动 Celery Worker 和 Celery Beat 服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 检查必要的环境变量
check_env_vars() {
    log_info "Checking environment variables..."

    required_vars=(
        "CELERY_BROKER_URL"
        "CELERY_RESULT_BACKEND"
        "DATABASE_URL"
        "MINIO_ENDPOINT"
        "MINIO_ACCESS_KEY"
        "MINIO_SECRET_KEY"
    )

    missing_vars=()

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done

    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        log_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        exit 1
    fi

    log_info "All required environment variables are set"
}

# 检查外部服务连接
check_services() {
    log_info "Checking external services..."

    # 检查 RabbitMQ
    if [[ $CELERY_BROKER_URL == *"amqp"* ]]; then
        log_debug "Checking RabbitMQ connection..."
        # 简单的连接检查，实际可以使用更复杂的检测
        rabbitmq_host=$(echo $CELERY_BROKER_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        if ping -c 1 "$rabbitmq_host" &> /dev/null; then
            log_info "✓ RabbitMQ server is reachable"
        else
            log_warn "⚠ RabbitMQ server may not be reachable"
        fi
    fi

    # 检查 Redis
    if [[ $CELERY_RESULT_BACKEND == *"redis"* ]]; then
        log_debug "Checking Redis connection..."
        redis_host=$(echo $CELERY_RESULT_BACKEND | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
        if ping -c 1 "$redis_host" &> /dev/null; then
            log_info "✓ Redis server is reachable"
        else
            log_warn "⚠ Redis server may not be reachable"
        fi
    fi

    # 检查 MinIO
    log_debug "Checking MinIO connection..."
    if ping -c 1 "$MINIO_ENDPOINT" &> /dev/null; then
        log_info "✓ MinIO server is reachable"
    else
        log_warn "⚠ MinIO server may not be reachable"
    fi
}

# 创建必要的目录
create_directories() {
    log_info "Creating necessary directories..."

    directories=(
        "/tmp/celery"
        "/var/log/celery"
        "/var/run/celery"
    )

    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            sudo mkdir -p "$dir"
            sudo chown $USER:$USER "$dir"
            log_info "Created directory: $dir"
        fi
    done
}

# 启动 Celery Worker
start_worker() {
    log_info "Starting Celery Worker..."

    # 停止现有的 worker（如果存在）
    pkill -f "celery.*worker" 2>/dev/null || true
    sleep 2

    # 启动 worker
    nohup celery -A src.scheduler.celery_app worker \
        --loglevel=${LOG_LEVEL:-INFO} \
        --queues=memory_sync,storage,maintenance \
        --concurrency=${CELERY_WORKER_CONCURRENCY:-4} \
        --max-tasks-per-child=${CELERY_WORKER_MAX_TASKS_PER_CHILD:-50} \
        --pidfile=/var/run/celery/worker.pid \
        --logfile=/var/log/celery/worker.log \
        --statedb=/var/run/celery/worker.state \
        > /dev/null 2>&1 &

    local worker_pid=$!
    echo $worker_pid > /var/run/celery/worker.pid

    log_info "Celery Worker started with PID: $worker_pid"
}

# 启动 Celery Beat
start_beat() {
    log_info "Starting Celery Beat..."

    # 停止现有的 beat（如果存在）
    pkill -f "celery.*beat" 2>/dev/null || true
    sleep 2

    # 启动 beat
    nohup celery -A src.scheduler.celery_app beat \
        --loglevel=${LOG_LEVEL:-INFO} \
        --schedule=/tmp/celery/celerybeat-schedule \
        --pidfile=/var/run/celery/beat.pid \
        --logfile=/var/log/celery/beat.log \
        > /dev/null 2>&1 &

    local beat_pid=$!
    echo $beat_pid > /var/run/celery/beat.pid

    log_info "Celery Beat started with PID: $beat_pid"
}

# 启动 Flower (可选)
start_flower() {
    if [[ "$START_FLOWER" == "true" ]]; then
        log_info "Starting Celery Flower..."

        # 停止现有的 flower（如果存在）
        pkill -f "celery.*flower" 2>/dev/null || true
        sleep 2

        # 启动 flower
        nohup celery -A src.scheduler.celery_app flower \
            --port=${FLOWER_PORT:-5555} \
            --basic_auth=${FLOWER_BASIC_AUTH:-admin:password} \
            --pidfile=/var/run/celery/flower.pid \
            > /dev/null 2>&1 &

        local flower_pid=$!
        echo $flower_pid > /var/run/celery/flower.pid

        log_info "Celery Flower started with PID: $flower_pid"
        log_info "Flower monitoring interface: http://localhost:${FLOWER_PORT:-5555}"
    fi
}

# 检查服务状态
check_status() {
    log_info "Checking service status..."

    services=("worker" "beat")

    for service in "${services[@]}"; do
        pid_file="/var/run/celery/${service}.pid"

        if [[ -f "$pid_file" ]]; then
            local pid=$(cat "$pid_file")
            if ps -p "$pid" > /dev/null 2>&1; then
                log_info "✓ Celery $service is running (PID: $pid)"
            else
                log_error "✗ Celery $service is not running (stale PID file)"
                rm -f "$pid_file"
            fi
        else
            log_error "✗ Celery $service is not running (no PID file)"
        fi
    done
}

# 停止所有服务
stop_services() {
    log_info "Stopping all Celery services..."

    services=("worker" "beat" "flower")

    for service in "${services[@]}"; do
        pid_file="/var/run/celery/${service}.pid"

        if [[ -f "$pid_file" ]]; then
            local pid=$(cat "$pid_file")
            if ps -p "$pid" > /dev/null 2>&1; then
                log_info "Stopping Celery $service (PID: $pid)..."
                kill -TERM "$pid"
                sleep 5

                # 如果进程仍然存在，强制杀死
                if ps -p "$pid" > /dev/null 2>&1; then
                    log_warn "Force killing Celery $service..."
                    kill -KILL "$pid"
                fi

                rm -f "$pid_file"
                log_info "✓ Celery $service stopped"
            else
                log_warn "Celery $service was not running"
                rm -f "$pid_file"
            fi
        fi
    done

    # 额外清理所有 celery 进程
    pkill -f "celery.*worker" 2>/dev/null || true
    pkill -f "celery.*beat" 2>/dev/null || true
    pkill -f "celery.*flower" 2>/dev/null || true

    log_info "All Celery services stopped"
}

# 显示帮助信息
show_help() {
    echo "Usage: $0 {start|stop|restart|status|help}"
    echo
    echo "Commands:"
    echo "  start    Start all Celery services"
    echo "  stop     Stop all Celery services"
    echo "  restart  Restart all Celery services"
    echo "  status   Show service status"
    echo "  help     Show this help message"
    echo
    echo "Environment Variables:"
    echo "  LOG_LEVEL                    Log level (DEBUG, INFO, WARNING, ERROR)"
    echo "  START_FLOWER                Start Flower monitoring (true/false)"
    echo "  FLOWER_PORT                  Flower monitoring port (default: 5555)"
    echo "  FLOWER_BASIC_AUTH            Flower basic auth (user:pass)"
    echo "  CELERY_WORKER_CONCURRENCY    Worker concurrency (default: 4)"
    echo "  CELERY_WORKER_MAX_TASKS_PER_CHILD  Max tasks per worker (default: 50)"
}

# 主函数
main() {
    case "${1:-start}" in
        start)
            log_info "Starting Memory Sync Scheduler..."
            check_env_vars
            check_services
            create_directories
            start_worker
            start_beat
            start_flower
            log_info "Memory Sync Scheduler started successfully!"
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 3
            main start
            ;;
        status)
            check_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Invalid command: $1"
            show_help
            exit 1
            ;;
    esac
}

# 切换到脚本所在目录
cd "$(dirname "$0")/.."

# 如果没有加载 .env 文件，尝试加载
if [[ -z "$DATABASE_URL" && -f ".env" ]]; then
    log_info "Loading environment from .env file..."
    set -a
    source .env
    set +a
fi

# 执行主函数
main "$@"