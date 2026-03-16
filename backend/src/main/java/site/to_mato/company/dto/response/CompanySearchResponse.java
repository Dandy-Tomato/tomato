package site.to_mato.company.dto.response;

import site.to_mato.company.entity.Company;

public record CompanySearchResponse(
        Long id,
        String name
) {
    public static  CompanySearchResponse from(Company company) {
        return new CompanySearchResponse(
                company.getId(),
                company.getName()
        );
    }
}
