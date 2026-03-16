package site.to_mato.company.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.web.bind.annotation.*;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.common.response.PageResponse;
import site.to_mato.company.dto.response.CompanySearchResponse;
import site.to_mato.company.service.CompanySearchService;

import java.util.List;

@RestController
@RequestMapping("/companies/search")
@RequiredArgsConstructor
public class CompanySearchController {

    private final CompanySearchService companySearchService;

    @GetMapping
    public ApiResponse<PageResponse<CompanySearchResponse>> searchCompanies(
            @RequestParam(name = "keyword", required = false) String keyword,
            Pageable pageable
    ) {
        Page<CompanySearchResponse> result = companySearchService.searchCompanies(keyword, pageable);

        return ApiResponse.ok(PageResponse.from(result));
    }

    @GetMapping("/auto-complete")
    public ApiResponse<List<CompanySearchResponse>> searchCompanySuggestions(
            @RequestParam(name = "keyword", required = false) String keyword
    ) {
        List<CompanySearchResponse> result = companySearchService.autocompleteCompanies(keyword);
        return ApiResponse.ok(result);
    }

}
