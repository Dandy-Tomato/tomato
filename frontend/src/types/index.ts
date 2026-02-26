// 공통으로 사용되는 TypeScript 타입과 인터페이스를 정의합니다.
export interface CommonResponse<T> {
    data: T;
    message: string;
    status: number;
}
