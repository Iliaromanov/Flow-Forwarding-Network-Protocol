up: 
	docker compose -f compose.yaml --profile routers up -d

down:
	docker compose -f compose.yaml --profile routers down -t 1

clean:
	-@echo "Cleaning..."
	-@rm -rf __pycache__

veryclean: clean down
	-@echo "Scubbing images..."
	-@docker image rm pycimage
	-@docker image prune -fa
