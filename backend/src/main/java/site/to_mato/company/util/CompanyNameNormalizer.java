package site.to_mato.company.util;

public class CompanyNameNormalizer {

    private static final String[] LEGAL_PREFIXES = {
            "㈜", "(주)", "주식회사", "유한회사"
    };

    public static String normalize(String name) {
        if (name == null) {
            return null;
        }

        String result = name.trim();

        // 법인 접두어 제거
        for (String prefix : LEGAL_PREFIXES) {
            result = result.replace(prefix, "");
        }

        // 괄호 제거
        result = result.replaceAll("[()]", "");

        // 공백 제거
        result = result.replaceAll("\\s+", "");

        // 특수문자 제거 (한글/영문/숫자 제외)
        result = result.replaceAll("[^가-힣a-zA-Z0-9]", "");

        // 소문자 통일
        result = result.toLowerCase();

        return result;
    }
}
