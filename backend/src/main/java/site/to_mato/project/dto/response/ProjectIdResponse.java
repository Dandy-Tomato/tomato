package site.to_mato.project.dto.response;

public record ProjectIdResponse(
        Long projectId
) {
    public static ProjectIdResponse of(Long projectId) {
        return new ProjectIdResponse(projectId);
    }
}
