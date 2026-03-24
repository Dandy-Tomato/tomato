package site.to_mato.batch.processor;

import org.springframework.batch.item.ItemProcessor;
import org.springframework.stereotype.Component;
import site.to_mato.batch.entity.CompanyStaging;
import site.to_mato.company.util.CompanyNameNormalizer;

@Component
public class CompanyStagingProcessor implements ItemProcessor<CompanyStaging, CompanyStaging> {

    @Override
    public CompanyStaging process(CompanyStaging item) throws Exception {

        String normalizedName = CompanyNameNormalizer.normalize(item.getName());
        item.updateSearchName(normalizedName);

        return item;
    }
}
