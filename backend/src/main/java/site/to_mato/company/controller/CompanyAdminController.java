package site.to_mato.company.controller;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import site.to_mato.company.service.CompanySearchService;

@RestController
@RequiredArgsConstructor
@RequestMapping("/admin/companies")
public class CompanyAdminController {

    private final CompanySearchService companySearchService;

    @PostMapping("/normalize-search-name")
    public ResponseEntity<Integer> normalizeSearchName() {

        int updatedCount = companySearchService.fillSearchNames();

        return ResponseEntity.ok(updatedCount);
    }

}
