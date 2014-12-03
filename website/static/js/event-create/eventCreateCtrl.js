/*global angular: false*/

angular.module('fpEvents.create', [])
	.controller('eventsCtrl', ['$scope', 'FileUpload',
            function ($scope, FileUploadFactory) {

			$scope.selectableMissionsTypes = [
				{
					id: '1',
					name: 'CO'
                    }, {
					id: '2',
					name: 'TvT'
                    }
                ];
			$scope.eventType = $scope.selectableMissionsTypes[0];

			$scope.uploadMissionImage = function () {
				var file = $scope.missionImageFile;
				var dfd = FileUploadFactory.uploadMissionImage(file);
				dfd.success(function ok(response) {
					$scope.eventImageUrl = response;
				}).error(function (e) {
					console.log(e);
				});
			};
    }]);