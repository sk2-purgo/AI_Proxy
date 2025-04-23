// src/main/java/com/example/purgoproxy/service/ApiKeyService.java
package com.example.purgoproxy.service;

import com.example.purgoproxy.entity.ApiKeyEntity;
import com.example.purgoproxy.repository.ApiKeyRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service @RequiredArgsConstructor
public class ApiKeyService {

    private final ApiKeyRepository repo;

    /** 유효한 키인지 검사 */
    public boolean isValid(String apiKey) {
        return repo.findByApiKeyAndStatus(apiKey, ApiKeyEntity.Status.ACTIVE)
                .isPresent();
    }

    /** 새 키 등록(관리자 용) */
    public ApiKeyEntity save(ApiKeyEntity entity) { return repo.save(entity); }
}
