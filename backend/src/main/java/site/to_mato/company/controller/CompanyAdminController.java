package site.to_mato.company.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import site.to_mato.common.response.ApiResponse;
import site.to_mato.company.service.CompanySearchService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/admin/companies")
public class CompanyAdminController {

    private final CompanySearchService companySearchService;

    @PostMapping("/normalize-search-name")
    public ApiResponse<Integer> normalizeSearchName() {

        int updatedCount = companySearchService.fillSearchNames();

        return ApiResponse.ok(updatedCount);
    }

}
