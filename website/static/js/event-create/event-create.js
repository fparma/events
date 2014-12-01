/*global angular: false*/

angular.module('fpEvents', ['fpEvents.create', 'fpEvents.slots'])
    .config(function ($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    });


angular.module('fpEvents.create', [])
    .controller('eventsCtrl', ['$scope',
            function ($scope) {

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
    .controller('slotsCtrl', ['$scope',
            function ($scope) {

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

            $scope.checkValidAndSubmit = function () {
                var data = angular.toJson({
                    eventType: $scope.eventType.name,
                    eventSlotsNumber: parseInt($scope.eventSlots, 10),
                    eventName: $scope.eventName,
                    eventNameFull: $scope.eventType.name + $scope.eventSlots + ' - ' + $scope.eventName,
                    eventDescription: $scope.eventDescription,
                    eventSlots: $scope.sideSlots
                });
                alert(JSON.stringify(JSON.parse(data), null, 4));
            };
    }]);