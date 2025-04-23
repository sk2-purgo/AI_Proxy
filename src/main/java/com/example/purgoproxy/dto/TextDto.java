package com.example.purgoproxy.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class TextDto {
    @NotBlank
    private String text;
}
