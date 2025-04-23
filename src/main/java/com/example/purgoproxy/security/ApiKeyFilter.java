package com.example.purgoproxy.security;

import com.example.purgoproxy.service.ApiKeyService;
import jakarta.servlet.*;
import jakarta.servlet.http.*;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

// src/main/java/com/example/purgoproxy/security/ApiKeyFilter.java
@RequiredArgsConstructor
@Component
public class ApiKeyFilter extends OncePerRequestFilter {

    private final ApiKeyService apiKeyService;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain)
            throws ServletException, IOException {

        String auth = request.getHeader("Authorization");
        String prefix = "Bearer ";

        if (auth == null || !auth.startsWith(prefix)) {
            System.out.println("Authorization 헤더 없음 또는 잘못됨");
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("Missing or invalid Authorization header");
            return;
        }

        String apiKey = auth.substring(prefix.length());
        if (!apiKeyService.isValid(apiKey)) {
            System.out.println("인증 실패한 API Key: " + apiKey);
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            response.getWriter().write("Invalid API Key");
            return;
        }

        chain.doFilter(request, response);
    }
}

