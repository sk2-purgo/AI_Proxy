package com.example.purgoproxy;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;

@SpringBootApplication
public class PurgoProxyApplication {

    public static void main(String[] args) {
        SpringApplication.run(PurgoProxyApplication.class, args);
    }
}
