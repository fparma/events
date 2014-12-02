/*global angular: false*/

angular.module('fpEvents', ['fpEvents.create', 'fpEvents.slots'])
    .config(['$interpolateProvider', '$httpProvider',
        function ($interpolateProvider, $httpProvider) {
            $interpolateProvider.startSymbol('[[');
            $interpolateProvider.endSymbol(']]');
            delete $httpProvider.defaults.headers.common["X-Requested-With"];
    }]).filter('capitalize', function () {
        return function (input) {
            return (!!input) ? input.replace(/([^\W_]+[^\s-]*) */g, function (txt) {
                return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
            }) : '';
        };
    }).factory('FileUploadFactory', ['$http', '$q', '$location',
        function ($http, $q, $location) {
            return {
                getPlayableUnitsFromFile: function (file) {
                    /*global FormData: false*/

                    var dfd = $q.defer();
                    var fd = new FormData();
                    fd.append('sqmFile', file);
                    $http.post('http://' + $location.host() + ':8080/api/parse-sqm-file', fd, {
                        transformRequest: angular.identity,
                        headers: {
                            'Content-Type': undefined
                        }
                    })
                        .success(function (response) {
                            if (response.data) {
                                dfd.resolve(response.data);
                            } else {
                                // failed to parse
                                dfd.reject(response.error);
                            }
                        })
                        .error(function (e) {
                            // server is down?
                            console.log(e);
                        });
                    return dfd.promise;
                },
                uploadMissionImage: function (imageFile) {

                    var dfd = $q.defer();
                    var fd = new FormData();
                    fd.append('file', imageFile);
                    $http.post('/upload', fd, {
                        transformRequest: angular.identity,
                        headers: {
                            'Content-Type': undefined
                        }
                    })
                        .success(function (urlForImage) {
                            dfd.resolve(urlForImage);
                        })
                        .error(function (e) {
                            dfd.reject();
                            console.log(e);
                            debugger;
                        });
                    return dfd.promise;

                }
            };
    }]).directive('fileModel', ['$parse',
        function ($parse) {
            return {
                restrict: 'A',
                link: function (scope, element, attrs) {
                    var model = $parse(attrs.fileModel);
                    var modelSetter = model.assign;

                    element.bind('change', function () {
                        scope.$apply(function () {
                            modelSetter(scope, element[0].files[0]);
                        });
                    });
                }
            };
}]);

angular.module('fpEvents.create', [])
    .controller('eventsCtrl', ['$scope', 'FileUploadFactory',
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
                FileUploadFactory.uploadMissionImage(file)
                    .then(function ok(data) {
                            $scope.eventImageUrl = data;
                        },
                        function error(e) {
                            debugger;
                        });
            };


    }]).directive('numbersOnly', function () {
        return {
            require: 'ngModel',
            restrict: 'A',
            link: function (scope, element, attrs, modelCtrl) {
                modelCtrl.$parsers.push(function (inputValue) {
                    if (inputValue === undefined) {
                        return '';
                    }
                    var transformedInput = Math.abs(inputValue.replace(/[^0-9+.]/g, '')) + '';
                    if (transformedInput.length > 2) {
                        transformedInput = (transformedInput[0] + transformedInput[1]);
                    }
                    if (transformedInput === '0') {
                        transformedInput = '';
                    }
                    if (transformedInput != inputValue) {
                        modelCtrl.$setViewValue(transformedInput);
                        modelCtrl.$render();
                    }

                    return transformedInput;
                });
            }
        };
    });


angular.module('fpEvents.slots', [])
    .controller('slotsCtrl', ['$scope', '$http', '$window', '$location', '$timeout', 'FileUploadFactory',
            function ($scope, $http, $window, $location, $timeout, FileUploadFactory) {

            function resetSides() {
                $scope.sideSlots = {
                    west: [],
                    east: [],
                    guer: [],
                    civ: []
                };
            }
            resetSides();

            // helper array to keep the map ordered
            $scope.orderedSides = [
                {
                    getGroups: function () {
                        return $scope.sideSlots.west;
                    },
                    displayName: 'Blufor',
                    sideName: 'west'
                },
                {
                    getGroups: function () {
                        return $scope.sideSlots.east;
                    },
                    displayName: 'Opfor',
                    sideName: 'east'
                },
                {
                    getGroups: function () {
                        return $scope.sideSlots.guer;
                    },
                    displayName: 'Independent',
                    sideName: 'guer'
                },
                {
                    getGroups: function () {
                        return $scope.sideSlots.civ;
                    },
                    displayName: 'Civilian',
                    sideName: 'civ'
                },
            ];

            $scope.editManually = function () {
                resetSides();
                $scope.addNewGroup('west');
            };

            $scope.updateSideSelection = function (e, side) {
                var isAdd = e.target.checked;
                if (isAdd) {
                    $scope.addNewGroup(side);
                } else {
                    //remove
                    $scope.sideSlots[side] = [];
                }
            };

            $scope.anySideHaveUnits = function () {
                return ['west', 'east', 'guer', 'civ'].some($scope.sideHasUnits);
            };

            $scope.sideHasUnits = function (side) {
                var slotSide = $scope.sideSlots[side];
                for (var key in slotSide) {
                    var units = slotSide[key].units;
                    if (units && units.length > 0) {
                        return true;
                    }
                }
                return false;
            };

            $scope.addNewGroup = function (side, name) {
                $scope.sideSlots[side].push({
                    name: name || 'Group',
                    side: side,
                    units: [{}, {}, {}, {}, {}, {}, {}, {}]
                });
            };

            $scope.deleteGroup = function (side, idx) {
                $scope.sideSlots[side].splice(idx, 1);
            };

            $scope.addUnitToGroup = function (group) {
                return group.units.push({});
            };

            $scope.removeUnitFromGroup = function (group) {
                return group.units.splice(group.length - 1, 1);
            };

            $scope.uploadSQMFile = function () {
                var file = $scope.sqmFile;
                FileUploadFactory.getPlayableUnitsFromFile(file)
                    .then(function ok(data) {
                            $timeout(function () {
                                $scope.sideSlots = data;
                            }, 0);
                        },
                        function error(e) {
                            debugger;
                        });
            };

            $scope.checkValidAndSubmit = function () {
                var slots = {};
                for (var i in $scope.sideSlots) {
                    if ($scope.sideSlots[i].length) {
                        slots[i] = $scope.sideSlots[i];
                    }
                }
                var data = angular.toJson({
                    eventType: $scope.eventType.name,
                    eventImageUrl: $scope.eventImageUrl,
                    eventSlotsNumber: parseInt($scope.eventSlots, 10),
                    eventName: $scope.eventName,
                    eventNameFull: $scope.eventType.name + $scope.eventSlots + ' - ' + $scope.eventName,
                    eventDescription: $scope.eventDescription,
                    eventSlots: slots
                });

                $http({
                    url: '/create',
                    method: 'POST',
                    data: data,
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                    .success(function (data, status, headers, config) {
                        console.log('success');
                        console.log(data);
                        //redirect
                        $window.location.href = ('http://' + $location.host() + ':' + $location.port());
                    })
                    .error(function (data, status, headers, config) {
                        console.log('error');
                        console.log(data);
                    });
            };
}]);