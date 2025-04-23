// src/main/java/com/example/purgoproxy/repository/ApiKeyRepository.java
package com.example.purgoproxy.repository;

import com.example.purgoproxy.entity.ApiKeyEntity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ApiKeyRepository extends JpaRepository<ApiKeyEntity, Long> {
    Optional<ApiKeyEntity> findByApiKeyAndStatus(String apiKey,
                                                 ApiKeyEntity.Status status);
}
