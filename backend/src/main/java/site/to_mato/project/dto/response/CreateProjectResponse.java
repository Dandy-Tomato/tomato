package site.to_mato.project.dto.response;

public record CreateProjectResponse(
        Long projectId
) {
    public static CreateProjectResponse of(Long projectId) {
        return new CreateProjectResponse(projectId);
    }
}
