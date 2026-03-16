package site.to_mato.company.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Pageable;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import site.to_mato.company.dto.response.CompanySearchResponse;
import site.to_mato.company.service.CompanySearchService;

import java.util.List;

@RestController
@RequestMapping("/companies/search")
@RequiredArgsConstructor
public class CompanySearchController {

    private final CompanySearchService companySearchService;

    @GetMapping
    public ResponseEntity<List<CompanySearchResponse>> searchCompanies(
            @RequestParam(name = "keyword", required = false) String keyword,
            Pageable pageable
    ) {
        List<CompanySearchResponse> result = companySearchService.searchCompanies(keyword, pageable);
        return ResponseEntity.ok(result);
    }

}
