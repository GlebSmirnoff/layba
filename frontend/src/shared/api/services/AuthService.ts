/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuthService {
    /**
     * Issue CSRF cookie (dev)
     * @returns any
     * @throws ApiError
     */
    public static authCsrf(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/auth/csrf/',
        });
    }
    /**
     * @returns any Email confirmed
     * @throws ApiError
     */
    public static authEmailConfirmCreate(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/email/confirm',
        });
    }
    /**
     * @returns void
     * @throws ApiError
     */
    public static authEmailSendCodeCreate(): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/email/send_code',
        });
    }
    /**
     * @returns void
     * @throws ApiError
     */
    public static authPhoneSendCodeCreate(): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/phone/send_code',
        });
    }
    /**
     * @returns any Authorized
     * @throws ApiError
     */
    public static authPhoneVerifyCreate(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/phone/verify',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static authSessionLoginCreate(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/session/login',
        });
    }
    /**
     * @returns any No response body
     * @throws ApiError
     */
    public static authSessionLogoutCreate(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/session/logout',
        });
    }
    /**
     * @returns any Apple profile
     * @throws ApiError
     */
    public static authSocialAppleCreate(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/social/apple',
        });
    }
    /**
     * @returns any Facebook profile
     * @throws ApiError
     */
    public static authSocialFacebookCreate(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/social/facebook',
        });
    }
    /**
     * @returns any Google profile
     * @throws ApiError
     */
    public static authSocialGoogleCreate(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/social/google',
        });
    }
}
