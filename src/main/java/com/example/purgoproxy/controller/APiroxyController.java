// src/main/java/com/example/purgoproxy/controller/AiProxyController.java
package com.example.purgoproxy.controller;   // ✅ 1. 패키지 경로

import com.example.purgoproxy.dto.TextDto;   // ✅ 1. import 경로
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api")
public class APiroxyController {

    private final RestTemplate restTemplate;   // RestTemplateConfig 에서 빈으로 등록됨

    @Value("${purgo.ai.base-url}")            // 예) http://localhost:5000
    private String flaskUrl;

    @PostMapping("/filter")
    public ResponseEntity<String> filter(@RequestBody TextDto dto) {

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        HttpEntity<TextDto> entity = new HttpEntity<>(dto, headers);

        // ✅ 2. 실제 Flask 엔드포인트
        String url = flaskUrl + "/analyze";

        return restTemplate.postForEntity(url, entity, String.class);
    }
}
