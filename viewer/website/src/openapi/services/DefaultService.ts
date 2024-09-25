/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProteinData } from '../models/ProteinData';
import type { SimilarityQuery } from '../models/SimilarityQuery';
import type { TaxonomyInfo } from '../models/TaxonomyInfo';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * Compute Similarity
     * @param requestBody
     * @returns ProteinData Successful Response
     * @throws ApiError
     */
    public static computeSimilarity(
        requestBody: SimilarityQuery,
    ): CancelablePromise<ProteinData> {
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
    /**
     * Taxonomy Info
     * @returns TaxonomyInfo Successful Response
     * @throws ApiError
     */
    public static taxonomyInfo(): CancelablePromise<TaxonomyInfo> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/taxonomy-info',
        });
    }
}
