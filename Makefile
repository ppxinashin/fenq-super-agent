.PHONY: help install dev-install run test clean docker-up docker-down

help:
	@echo "Fenq Super Agent - Makefile 命令"
	@echo ""
	@echo "可用命令:"
	@echo "  make install        - 安装生产依赖"
	@echo "  make dev-install    - 安装开发依赖"
	@echo "  make run            - 启动服务"
	@echo "  make docker-up      - 启动 Docker 容器（PostgreSQL + Redis）"
	@echo "  make docker-down    - 停止 Docker 容器"
	@echo "  make clean          - 清理临时文件"
	@echo "  make test           - 运行测试（暂未实现）"

install:
	pip install -r requirements.txt
	playwright install chromium

dev-install: install
	pip install pytest pytest-asyncio black flake8 mypy

run:
	python main.py

docker-up:
	docker-compose up -d
	@echo "等待服务启动..."
	@sleep 5
	@echo "PostgreSQL 和 Redis 已启动"
	@echo "PostgreSQL: localhost:5432"
	@echo "Redis: localhost:6379"

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build

test:
	@echo "测试功能暂未实现"

