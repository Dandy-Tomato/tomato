package site.to_mato.company.service;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import site.to_mato.company.dto.response.CompanySearchResponse;
import site.to_mato.company.repository.CompanyRepository;

import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class CompanySearchService {

    private final CompanyRepository companyRepository;

    public List<CompanySearchResponse> searchCompanies(String keyword, Pageable pageable) {
        if (keyword == null || keyword.trim().isEmpty()) {
            return Collections.emptyList();
        }

        return companyRepository.findBySearchNameContainingIgnoreCase(keyword, pageable).stream()
                .map(CompanySearchResponse::from)
                .collect(Collectors.toList());
    }

}
