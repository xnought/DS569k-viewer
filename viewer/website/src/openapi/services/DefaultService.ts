/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EmbeddingsData } from '../models/EmbeddingsData';
import type { ProteinCLIPQuery } from '../models/ProteinCLIPQuery';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Compute Similarity
     * @param requestBody
     * @returns EmbeddingsData Successful Response
     * @throws ApiError
     */
    public static computeSimilarity(
        requestBody: ProteinCLIPQuery,
    ): CancelablePromise<EmbeddingsData> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/proteinclip',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
