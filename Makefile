MONGO_CONTAINER=mongo_db  # Change if your container name is different

.PHONY: fix-mongo
fix-mongo:
	@echo "🔧 Updating MongoDB configuration..."
	@docker exec -it $(MONGO_CONTAINER) bash -c "echo 'net:\n  bindIp: 0.0.0.0' > /etc/mongod.conf"
	@echo "✅ Configuration updated. Restarting MongoDB..."
	@docker restart $(MONGO_CONTAINER)
	@echo "🚀 MongoDB is now accessible from localhost!"

bash:
	docker exec -it fastapi_app bash

ipconf:
	ip addr show docker0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1

mongoip:
	docker inspect mongo_db | grep "IPAddress"

#docker exec -it fastapi-react-mongodb-docker-backend-1 bash 