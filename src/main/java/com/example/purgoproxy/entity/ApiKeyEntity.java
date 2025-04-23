package com.example.purgoproxy.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity @Table(name = "api_keys")
@Getter @Setter @NoArgsConstructor
public class ApiKeyEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "api_key", length = 64, nullable = false, unique = true)
    private String apiKey;

    @Enumerated(EnumType.STRING)
    private Status status = Status.ACTIVE;

    private String memo;

    public enum Status { ACTIVE, REVOKED }
}
