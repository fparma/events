/*global angular: false*/

angular.module('fpEvents', ['fpEvents.create', 'fpEvents.slots'])

.config(['$interpolateProvider', '$httpProvider',
        function ($interpolateProvider, $httpProvider) {
		$interpolateProvider.startSymbol('[[');
		$interpolateProvider.endSymbol(']]');
		delete $httpProvider.defaults.headers.common["X-Requested-With"];

    }]).factory('FileUpload', ['$http', '$q', '$location',
        function ($http, $q, $location) {

		function getFormHeaders() {
			return {
				'Content-Type': undefined
			};
		}

		return {
			getPlayableUnitsFromFile: function (file) {
				/*global FormData: false*/

				var dfd = $q.defer();
				var fd = new FormData();
				fd.append('sqmFile', file);
				$http.post('http://' + $location.host() + ':8080/api/parse-sqm-file', fd, {
					transformRequest: angular.identity,
					headers: getFormHeaders()
				}).success(function (response) {
					if (response.data) {
						dfd.resolve(response.data);
					} else {
						// failed to parse
						dfd.reject(response.error);
					}
				}).error(function (e) {
					// server is down?
					console.log(e);
				});
				return dfd.promise;
			},

			uploadMissionImage: function (imageFile) {
				var fd = new FormData();
				fd.append('file', imageFile);
				return $http.post('/upload', fd, {
					transformRequest: angular.identity,
					headers: getFormHeaders()
				});

			}
		};

    }]).service('EventService', ['$http', '$window', '$location',
        function ($http, $window, $location) {
		// TODO should redirect really happen here
		this.createNewEvent = function (data) {
			return $http({
				url: '/create',
				method: 'POST',
				data: data,
				headers: {
					'Content-Type': 'application/json'
				}
			}).success(function (data) {
				console.log('success');
				console.log(data);
				//redirect
				$window.location.href = ('http://' + $location.host() + ':' + $location.port());
			}).error(function (data) {
				console.log('error');
				console.log(data);
			});
		};
}]);